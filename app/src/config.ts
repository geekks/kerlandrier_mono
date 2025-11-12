import { DateTime } from "luxon";
const today = DateTime.now().set({ hour: 0, minute: 0, second: 0, millisecond: 0 });

interface RuntimeConfig {
  API_URL: string;
  OA_SLUG: string;
  OA_UID: string;
  OA_PUBLIC_KEY: string;
}

let runtimeConfig: RuntimeConfig | null = null;

// Load configuration from config.json
const loadConfig = async (): Promise<RuntimeConfig> => {
  if (runtimeConfig === null) {
    const response = await fetch('/config.json');
    if (!response.ok) {
      throw new Error(`Failed to load config.json: ${response.status}`);
    }
    runtimeConfig = await response.json();
  }
  return runtimeConfig!; // We know it's not null after the if block
};

export const getConfig = async () => {
  return await loadConfig();
};

export let OA_SLUG: string = '';
export let KERLANDRIER_API_URL: string = '';
export let API_URL: string = '';

const MAX_EVENTS = 400
export const AREA_FILTERS = ["aven", "cornouaille", "bretagne"];

const includeFields = ["uid", "uid-externe", "slug", "title", "onlineAccessLink", "registration", "status", "keywords", "dateRange", "location.description", "firstTiming", "nextTiming", "lastTiming", "longDescription", "description", "location.name", "location.city", "keywords", "timings"];
const fieldsParam = includeFields.map(field => `includeFields[]=${field}`).join("&")

export let defaultQuery: string = '';
export let editoQuery: string = '';

// Initialize all exports from config.json
loadConfig().then(config => {
  OA_SLUG = config.OA_SLUG;
  KERLANDRIER_API_URL = config.API_URL;
  API_URL = config.API_URL;
  
  const OA_BASE_URL = `https://api.openagenda.com/v2/agendas/${config.OA_UID}/events`;
  const DEFAULT_PARAMS = {
    detailed: "0",
    key: config.OA_PUBLIC_KEY,
    size: MAX_EVENTS.toString(),
    monolingual: "fr",
  };
  
  defaultQuery = `${OA_BASE_URL}?${new URLSearchParams(DEFAULT_PARAMS).toString()}&relative[]=current&relative[]=upcoming&${fieldsParam}`;
  editoQuery = `${OA_BASE_URL}?${new URLSearchParams(DEFAULT_PARAMS).toString()}&timings[gte]=${today.toUTC()}&timings[lte]=${today.plus({ days: 15 }).toUTC()}&${fieldsParam}&sort=timings.asc`;
}).catch(error => {
  console.error('Failed to initialize config:', error);
});
