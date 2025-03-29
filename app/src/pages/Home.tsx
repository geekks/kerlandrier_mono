import { useState } from "react";
import ky from "ky";
import { useQuery } from "@tanstack/react-query";
import { AREA_FILTERS, defaultQuery } from "../config";
import type {
	OpenAgendaEvent,
	OpenAgendaEventsReponse,
} from "../types/OpenAgenda";
import { EventsList } from "../components/EventsList";
import { SelectDate } from "../SelectDate";
import { SelectAreas } from "../SelectAreas";
import { Link } from "react-router-dom";
import { DateTime } from "luxon";

const loadEvents = async (): Promise<OpenAgendaEventsReponse> => {
	const response: OpenAgendaEventsReponse = await ky(defaultQuery).json();
	return response;
};

const Home = () => {
	const [selectedStartDate, setSelectedStartDate] = useState<Date | null>(null);
	const [selectedEndDate, setSelectedEndDate] = useState<Date | null>(null);
	const [selectedAreas, setSelectedAreas] = useState<string[]>([]);
	const {
		data: { events: oaEventsResponse },
		isLoading,
		isError,
		error,
	} = useQuery({
		queryKey: ["events"],
		queryFn: loadEvents,
		initialData: { events: [], total: 0 },
	});

	const handleDateChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
		if (!event.target.value) {
			setSelectedStartDate(null);
			setSelectedEndDate(null);
			return;
		}
		const selectedDateValue = new Date(event.target.value);
		setSelectedStartDate(selectedDateValue);
		const endOfMonth = new Date(
			selectedDateValue.getFullYear(),
			selectedDateValue.getMonth() + 1,
			0,
		);
		setSelectedEndDate(endOfMonth);
	};

	const toggleArea = (event: React.MouseEvent<HTMLButtonElement>) => {
		const areaName = event.currentTarget.name;
		if (selectedAreas.includes(areaName)) {
			setSelectedAreas(selectedAreas.filter((area) => area !== areaName));
		} else {
			setSelectedAreas([...selectedAreas, areaName]);
		}
	};

	type getEventsOptions = {
		isLongEvents: boolean;
	};

	const getEvents = ({
		isLongEvents = false,
	}: getEventsOptions): OpenAgendaEvent[] => {
		if (oaEventsResponse) {
			const longEvents = oaEventsResponse
				.filter((d) => d["uid-externe"] !== "DUPLICATE")
				.filter((d) => d.dateRange.includes("-"))
				.filter((d) => {
					if (selectedAreas.length === 0) return true;
					return d.location.description.fr
						? selectedAreas.includes(d.location.description.fr.toLowerCase())
						: true;
				})
				.filter((d) => {
					if (!selectedStartDate || !selectedEndDate) return true;
					return (
						selectedStartDate <= new Date(d.lastTiming.end) &&
						selectedEndDate >= new Date(d.firstTiming.begin)
					);
				});

			if (isLongEvents) return longEvents;

			let shortEvents = oaEventsResponse
				.filter((d) => d["uid-externe"] !== "DUPLICATE")
				.filter((d) => !d.dateRange.includes("-"))
				.filter((d) => {
					if (selectedAreas.length === 0) return true;
					return d.location.description.fr
						? selectedAreas.includes(d.location.description.fr.toLowerCase())
						: true;
				})
				.filter((d) => {
					if (!selectedStartDate || !selectedEndDate) return true;
					return (
						selectedStartDate <= new Date(d.lastTiming.end) &&
						selectedEndDate >= new Date(d.firstTiming.begin)
					);
				});

			const longEventsNextTiming = longEvents.map((d) => {
				let newDateRange = DateTime.fromISO(d.nextTiming.begin, {
					zone: "Europe/Paris",
				})
					.setLocale("fr")
					.toFormat("cccc d LLLL");
				newDateRange =
					newDateRange.charAt(0).toUpperCase() + newDateRange.slice(1);
				return { ...d, dateRange: newDateRange };
			});

			shortEvents.push(...longEventsNextTiming);
			shortEvents = shortEvents.sort(
				(a: OpenAgendaEvent, b: OpenAgendaEvent) => {
					const dateA = new Date(a.nextTiming.begin);
					const dateB = new Date(b.nextTiming.begin);
					return dateA.getTime() - dateB.getTime();
				},
			);
			return shortEvents;
		}
		return [];
	};

	if (isLoading) {
		return <div>Loading...</div>;
	}

	if (isError) {
		return (
			<div>
				Error: {error.name} {error.message}
			</div>
		);
	}

	return (
		<div>
			<header>
				<div id="title">
					<div id="info-container">
						<h1>Kerlandrier.cc</h1>
						<p id="description">
							Agenda collaboratif des évènements autour de Concarneau
						</p>
						<span id="infos-link">
							{" "}
							<Link to="/diwarbenn">
								Ajoutez un événement ou en savoir plus
							</Link>{" "}
						</span>
					</div>

					<div id="qr-container">
						<img id="qr" src="/qr_diwar-benn.svg" alt="Kerlandrier QR code" />
						<div>
							<span>Retrouvez-nous</span>
							<span> en ligne</span>
						</div>
					</div>
					<div id="filters-container">
						<SelectDate handleDateChange={handleDateChange} />
						<div id="filters">
							{AREA_FILTERS.map((area, index) => (
								<SelectAreas
									id={`area-${index + 1}`}
									key={area}
									toggleArea={toggleArea}
									name={area}
									className={`${selectedAreas.includes(area) ? "selected" : ""}`}
								/>
							))}
						</div>
					</div>
				</div>
			</header>
			<EventsList
				longEvents={false}
				events={getEvents({ isLongEvents: false })}
			/>
			<h1 id="exposection">Expositions / Festivals</h1>
			<EventsList
				longEvents={true}
				events={getEvents({ isLongEvents: true })}
			/>
		</div>
	);
};

export default Home;
