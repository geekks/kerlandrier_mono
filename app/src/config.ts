import { DateTime } from "luxon";
const today = DateTime.now().set({ hour: 0, minute: 0, second: 0, millisecond: 0 });

export const KERLANDRIER_API_URL = import.meta.env.VITE_API_URL || 'https://api.kerlandrier.cc' as string
export const OA_SLUG = import.meta.env.VITE_OA_SLUG as string
export const API_URL = import.meta.env.VITE_API_URL || 'https://api.kerlandrier.cc'

const OA_UID = import.meta.env.VITE_OA_UID
const OA_PUBLIC_KEY = import.meta.env.VITE_OA_PUBLIC_KEY
const OA_BASE_URL = `https://api.openagenda.com/v2/agendas/${OA_UID}/events`

const MAX_EVENTS = 400
export const AREA_FILTERS = ["aven", "cornouaille", "bretagne"];

const includeFields = ["uid", "slug", "title", "onlineAccessLink", "status", "keywords", "dateRange", "location.description", "firstTiming", "nextTiming", "lastTiming", "longDescription", "description", "location.name", "location.city", "keywords", "timings"];
const fieldsParam = includeFields.map(field => `includeFields[]=${field}`).join("&")
const DEFAULT_PARAMS = {
  detailed: "0",
  key: OA_PUBLIC_KEY,
  size: MAX_EVENTS.toString(),
  monolingual: "fr",
};

export const defaultQuery = `${OA_BASE_URL}?${new URLSearchParams(DEFAULT_PARAMS).toString()}&relative[]=current&relative[]=upcoming&${fieldsParam}`;
export const editoQuery = `${OA_BASE_URL}?${new URLSearchParams(DEFAULT_PARAMS).toString()}&timings[gte]=${today.toUTC()}&timings[lte]=${today.plus({ days: 30 }).toUTC()}&${fieldsParam}&sort=lastTiming.asc`;