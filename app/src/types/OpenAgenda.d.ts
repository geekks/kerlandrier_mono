type timing = {
  begin: string;
  end: string
}
export type OpenAgendaEvent = {
  uid: string;
  "uid-externe": string;
  slug: string;
  title: string;
  onlineAccessLink: string;
  registration: {[key:  string]: { value: string }}[];
  status: number;
  keywords: string[];
  dateRange: string;
  location: {
    description: { fr?: string };
    name: string;
    city: string
  }
  firstTiming: timing;
  nextTiming: timing;
  lastTiming: timing;
  longDescription: string;
  description: string;
  keyword: string;
  timings: timing[]
}

export type OpenAgendaEditoItem = OpenAgendaEvent & {
  firstTimingDate: string | undefined;
  firstTimingTimeStart: string | undefined;
  firstTimingTimeEnd: string | undefined;
  hasChanged: boolean
}

export type OpenAgendaEventsRequest = {
  [key: string]: any
}
export type OpenAgendaEventsReponse = {
  total: number;
  events: OpenAgendaEvent[];
}

export type OpenAgendaEditoResponse = {
  total: number;
  events: OpenAgendaEditoItem[]
  after?: string;
}

// TODO: Right values
export enum OpenAgendaStatus {
  FULL = 5,
  CANCELLED = 6
}

export enum HiddenStatus {
  "DUPLICATE" = "DUPLICATE",
}