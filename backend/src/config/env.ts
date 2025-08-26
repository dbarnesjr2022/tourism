// backend/src/config/env.ts
import 'dotenv/config';

function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env: ${name}`);
  return v;
}

export const ENV = {
  MOCK: (process.env.MOCK ?? 'true').toLowerCase() === 'true',
  RAPIDAPI_KEY: process.env.RAPIDAPI_KEY ?? '',
  HOSTS: {
    HOTELS: process.env.RAPIDAPI_HOST_HOTELS ?? 'hotels4.p.rapidapi.com',
    BOOKING: process.env.RAPIDAPI_HOST_BOOKING ?? 'booking-com.p.rapidapi.com',
    PRICELINE: process.env.RAPIDAPI_HOST_PRICELINE ?? 'priceline-com.p.rapidapi.com',
    TRIPADVISOR: process.env.RAPIDAPI_HOST_TRIPADVISOR ?? 'tripadvisor16.p.rapidapi.com',
  },
};
