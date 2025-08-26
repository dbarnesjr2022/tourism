// backend/src/scripts/smoke_rapid.ts
import { rapidGet } from '../lib/rapid';
import { ENV } from '../config/env';

async function main() {
  const hotels = await rapidGet<any>({
    host: ENV.HOSTS.HOTELS,
    url: '/properties/get-hotel-photos',
    query: { id: '1178275040' },
    cacheKey: 'hotels_photos_1178275040',
  });

  const booking = await rapidGet<any>({
    host: ENV.HOSTS.BOOKING,
    url: '/v1/attractions/calendar',
    query: { attraction_id: 'PRFZkGSVnM5d', currency: 'AED', locale: 'en-gb' },
    cacheKey: 'booking_attractions_PRFZkGSVnM5d',
  });

  const priceline = await rapidGet<any>({
    host: ENV.HOSTS.PRICELINE,
    url: '/cars/location/search',
    query: { q: 'Seattle' },
    cacheKey: 'priceline_cars_Seattle',
  });

  const trip = await rapidGet<any>({
    host: ENV.HOSTS.TRIPADVISOR,
    url: '/api/v1/restaurant/searchRestaurants',
    query: { locationId: '304554' },
    cacheKey: 'tripadvisor_restaurants_304554',
  });

  console.log('OK:', {
    hotels_count: hotels?.roomGallery?.length ?? hotels?.length ?? 0,
    booking_status: booking?.status ?? 'ok',
    priceline_items: Array.isArray(priceline?.results) ? priceline.results.length : 0,
    trip_results: Array.isArray(trip?.data) ? trip.data.length : 0,
  });
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
