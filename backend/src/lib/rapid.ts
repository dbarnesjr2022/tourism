// backend/src/lib/rapid.ts
import { ENV } from '../config/env';
import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';

type RapidOpts = {
  host: string;
  url: string; // e.g. "/properties/get-hotel-photos?id=1178275040"
  query?: Record<string, string | number | boolean | undefined>;
  cacheKey?: string;
};

const CACHE_DIR = path.join(process.cwd(), 'data', 'raw', 'rapidapi');
fs.mkdirSync(CACHE_DIR, { recursive: true });

function buildUrl(host: string, url: string, query?: RapidOpts['query']) {
  const qs = query
    ?
      '?' +
      Object.entries(query)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : '';
  return `https://${host}${url}${qs}`;
}

export async function rapidGet<T>({ host, url, query, cacheKey }: RapidOpts): Promise<T> {
  const full = buildUrl(host, url, query);
  const cachePath = cacheKey ? path.join(CACHE_DIR, `${cacheKey}.json`) : undefined;

  if (ENV.MOCK) {
    if (cachePath && fs.existsSync(cachePath)) {
      const raw = fs.readFileSync(cachePath, 'utf8');
      return JSON.parse(raw) as T;
    }
    throw new Error(`MOCK=true but no cache found for ${full} (cacheKey required in mock mode)`);
  }

  if (!ENV.RAPIDAPI_KEY) throw new Error('RAPIDAPI_KEY not set in env');

  const res = await fetch(full, {
    headers: {
      'x-rapidapi-host': host,
      'x-rapidapi-key': ENV.RAPIDAPI_KEY,
    },
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`RapidAPI error ${res.status} ${res.statusText} for ${full}\n${body}`);
  }

  const data = (await res.json()) as T;
  if (cachePath) fs.writeFileSync(cachePath, JSON.stringify(data, null, 2));
  return data;
}
