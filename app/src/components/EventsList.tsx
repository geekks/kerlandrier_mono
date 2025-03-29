// import type React from "react";
import type { OpenAgendaEvent } from "../types/OpenAgenda";
import { OA_SLUG } from "../config";
import "../utils/toTitleCase";
interface EventsListProps {
	events: OpenAgendaEvent[];
	longEvents: boolean;
}
export const EventsList = ({ events, longEvents }: EventsListProps) => {
	const EventsReactElements: React.ReactNode[] = [];
	const formatDateHeader = (day: string) => {
		return (
			<div className="date-header">
				<div className="sticky-date">
					<h4>{day}</h4>
					<p>░░░░░░░░░</p>
				</div>
			</div>
		);
	};

	const formatEventFields = (event: OpenAgendaEvent) => {
		const oaLink = `https://openagenda.com/fr/${OA_SLUG}/contribute/event/${event.uid}`;
		const redirectLink = event.onlineAccessLink
			? event.onlineAccessLink
			: event.registration
				? event.registration
				: oaLink;
		const nextTiming = event.nextTiming ? (
			<div className="time-tag">
				<a
					href={oaLink}
					className="hidden-link"
					target="_blank"
					rel="noreferrer"
				>
					{event.nextTiming.begin.split("T")[1].slice(0, 5)}
				</a>
			</div>
		) : null;

		const status =
			event.status === 5 ? "ANNULE" : event.status === 6 ? "COMPLET" : "";

		const keywords = event.keywords?.map((k, i) =>
			k ? (
				<div className="tag" key={`${event.slug}-${i}`}>
					{" "}
					#{k}{" "}
				</div>
			) : null,
		);

		const title = (
			<h2 className={`card-title ${status}`}>
				{status ? <span>[{status}]</span> : null}
				<a href={redirectLink} target="_blank" rel="noreferrer">
					{event.title.toLowerCase().toTitleCase()}
				</a>
			</h2>
		);

		const location = (
			<h3>
				⟜{event.location.name}, {event.location.city}
			</h3>
		);

		return { nextTiming, keywords, title, location };
	};

	const aggregatePerDay = (events: OpenAgendaEvent[]) => {
		return events.reduce(
			(days, event) => {
				const d = event.dateRange.split(",")[0];
				if (!days[d]) days[d] = [];
				days[d].push(event);
				return days;
			},
			{} as { [key: string]: OpenAgendaEvent[] },
		);
	};

	const addDayContent = (events: OpenAgendaEvent[], day: string) => {
		EventsReactElements.push(
			<div className="dateAndEvents" key={day}>
				{formatDateHeader(day)}
				<div className="evenements">
					{events.map((event) => {
						const { nextTiming, keywords, title, location } =
							formatEventFields(event);
						return (
							<span
								className="evenement"
								key={event.slug}
								title={event.longDescription ?? event.description}
							>
								<div className="tag-container">
									{nextTiming} {keywords}
								</div>
								{title}
								{location}
							</span>
						);
					})}
				</div>
			</div>,
		);
	};

	const eventsDayAgg = aggregatePerDay(events);
	for (const day in eventsDayAgg) {
		const events = eventsDayAgg[day];
		if (events.length === 0) continue;
		addDayContent(events, day);
	}

	// Add comment and link  to reach long events moved to bottom of page
	if (!longEvents && EventsReactElements.length >= 3) {
		const advertDiv = (
			<div id="expoadvert">
				{" "}
				Les longs évènements (expos, festival) sont{" "}
				<a href="#exposection">en bas de page</a>{" "}
			</div>
		);
		EventsReactElements.splice(2, 0, advertDiv);
	}

	return EventsReactElements;
};
