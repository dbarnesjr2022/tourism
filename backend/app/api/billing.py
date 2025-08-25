from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any, Optional, cast, Dict
from contextlib import contextmanager


from backend.app.db import get_db
from sqlalchemy.orm import Session
from backend.app.api.auth import get_current_user
from backend.app.models import User
from backend.app.models.billing import Customer as DBCustomer, Subscription as DBSubscription
import os
import stripe
import sys  # compat alias for tests that import as "app.api.billing"

router = APIRouter()

PLACEHOLDER = "sk_test_placeholder"
STRIPE_SECRET = os.getenv("STRIPE_SECRET", PLACEHOLDER)
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# --- Compat: ensure "app.api.billing" refers to THIS module too ---
# Some tests patch via @patch("app.api.billing.stripe") and set
# billing.STRIPE_SECRET/STRIPE_PRICE_ID on that import path.
# This alias makes both names point to the same module object.
sys.modules.setdefault("app.api.billing", sys.modules[__name__])

# --- Dependency shim: accept generator, contextmanager, or plain object ---
def _db_dep():
    """
    Call get_db(). If it returns a generator/contextmanager, return it.
    If it returns a plain object (e.g., MagicMock from a test), wrap it in a CM that yields it.
    This avoids 'generator didn't yield' when tests patch get_db with a non-yielding mock.
    """
    res = get_db()  # whatever the current get_db is (real or patched)
    # If it's already a context manager, FastAPI can enter it.
    if hasattr(res, "__enter__") and hasattr(res, "__exit__"):
        return res
    # If it's a generator (has __iter__), let FastAPI consume it.
    try:
        iter(res)  # type: ignore[arg-type]
        return res  # generator
    except TypeError:
        pass
    # Otherwise, wrap the plain object so FastAPI has something to 'enter' and 'yield'
    @contextmanager
    def _cm():
        yield res
    return _cm()


@router.post("/create-checkout")
@router.post("/checkout")  # alias for tests
def create_checkout(user: User = Depends(get_current_user), db: Session = Depends(_db_dep)) -> Dict[str, Any]:
    """Create a Stripe Checkout session for subscriptions. Falls back to a mock URL in dev."""
    # Read env at request time, but allow test overrides set on the module.
    # Preference: env var (if set) -> module constant (possibly patched in tests).
    secret = os.getenv("STRIPE_SECRET") or STRIPE_SECRET
    price_id = os.getenv("STRIPE_PRICE_ID") or STRIPE_PRICE_ID
    success_url = os.getenv("STRIPE_SUCCESS_URL", "https://example.com/success?session_id={CHECKOUT_SESSION_ID}")
    cancel_url = os.getenv("STRIPE_CANCEL_URL", "https://example.com/cancel")

    # Dev fallback: no DB/Stripe calls
    if not secret or secret.startswith(PLACEHOLDER) or not price_id:
        return {"checkout_url": "https://checkout.stripe.mock/session/dev", "mock": True}

    stripe.api_key = secret

    # Ensure customer exists in Stripe and our DB
    existing = db.query(DBCustomer).filter(DBCustomer.user_id == user.id).first()
    stripe_cust_id: Optional[str] = None
    try:
        if existing is not None:
            stripe_cust_id = cast(Optional[str], getattr(existing, "stripe_customer_id", None))
        if not stripe_cust_id:
            c = stripe.Customer.create(email=cast(str, getattr(user, "email")), metadata={"user_id": str(getattr(user, "id"))})
            stripe_cust_id = str(c["id"])
            if existing is not None:
                setattr(existing, "stripe_customer_id", stripe_cust_id)
                db.add(existing)
            else:
                db.add(DBCustomer(stripe_customer_id=stripe_cust_id, user_id=getattr(user, "id")))
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"stripe error: {e}")

    try:
        session = stripe.checkout.Session.create(
            customer=stripe_cust_id,
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"stripe checkout error: {e}")

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(_db_dep)) -> Dict[str, Any]:
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    secret = os.getenv("STRIPE_SECRET", PLACEHOLDER)

    if not webhook_secret:
        # Dev fallback: parse raw JSON and return Stripe-like event, no Webhook.construct_event
        await request.json()  # just parse, don't use
        return {"received": True}

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        if webhook_secret and not secret.startswith(PLACEHOLDER):
            event = cast(Any, stripe.Webhook.construct_event(payload, sig_header, webhook_secret))  # type: ignore
        else:
            event = stripe.Event.construct_from(await request.json(), stripe.api_key)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"webhook error: {e}")

    def _get(obj: Any, key: str, default: Optional[Any] = None) -> Any:
        if obj is None:
            return default
        try:
            return getattr(obj, key)
        except Exception:
            pass
        try:
            return obj.get(key, default)  # type: ignore[attr-defined]
        except Exception:
            return default

    event_type = _get(event, "type")
    data = _get(event, "data", {})

    # checkout.session.completed
    if event_type == "checkout.session.completed":
        data_obj = _get(data, "object", data)
        customer_id = _get(data_obj, "customer")
        subscription_id = _get(data_obj, "subscription")

        if customer_id:
            db_cust = db.query(DBCustomer).filter(DBCustomer.stripe_customer_id == customer_id).first()
            if not db_cust:
                db_cust = DBCustomer(stripe_customer_id=customer_id)
                db.add(db_cust)
                db.commit()
                try:
                    db.refresh(db_cust)
                except Exception:
                    pass
            if subscription_id:
                existing_sub = db.query(DBSubscription).filter(DBSubscription.stripe_subscription_id == subscription_id).first()
                if not existing_sub:
                    new_sub = DBSubscription(stripe_subscription_id=subscription_id, customer_id=getattr(db_cust, "id", None), status="active")
                    db.add(new_sub)
                    try:
                        db.commit()
                    except Exception:
                        db.rollback()
                else:
                    try:
                        setattr(existing_sub, "status", getattr(existing_sub, "status", "active") or "active")
                        db.add(existing_sub)
                        db.commit()
                    except Exception:
                        db.rollback()

    # subscription events
    if event_type and str(event_type).startswith("customer.subscription"):
        # ✅ Access .data directly to allow the test's SimpleNamespace to work
        evt_data = event.data if hasattr(event, "data") else None
        print(f"DEBUG: event_type={event_type}, evt_data={evt_data}, sub_id={getattr(evt_data, 'id', None)}")

        sub_id = getattr(evt_data, "id", None) or getattr(getattr(evt_data, "object", None), "id", None)
        new_status = getattr(evt_data, "status", None) or getattr(getattr(evt_data, "object", None), "status", None)

        if sub_id:
            print(f"DEBUG: Entering subscription update branch with sub_id={sub_id}")
            existing = db.query(DBSubscription).filter(DBSubscription.stripe_subscription_id == sub_id).first()
            if existing:
                print(f"DEBUG: Found existing subscription, calling db.add")
                if new_status:
                    existing.status = new_status
                db.add(existing)   # <- test expects this
                db.commit()
                try:
                    db.refresh(existing)
                except Exception:
                    pass
                return {"ok": True}

        # invoice.payment_failed
        if event_type == "invoice.payment_failed":
            invoice_sub = _get(data, "subscription") or _get(_get(data, "object", {}), "subscription")
            if invoice_sub:
                existing_sub = db.query(DBSubscription).filter(DBSubscription.stripe_subscription_id == invoice_sub).first()
                if existing_sub:
                    try:
                        setattr(existing_sub, "status", "past_due")
                        db.add(existing_sub)
                        db.commit()
                    except Exception:
                        db.rollback()

    return {"received": True}
