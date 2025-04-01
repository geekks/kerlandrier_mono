import { useQuery } from "@tanstack/react-query";
import { ImSpinner7 } from "react-icons/im";
import { editoQuery } from "../config";
import { DateTime } from "luxon";
import "../layout.css";
import type {
	OpenAgendaEditoItem,
	OpenAgendaEditoResponse,
} from "../types/OpenAgenda";
import { Autocomplete, Chip, TextField, Tooltip } from "@mui/material";
import { useCallback } from "react";
import React from "react";

const fetchEditoEvents = async (): Promise<OpenAgendaEditoItem[]> => {
	const response = await fetch(editoQuery);
	if (!response.ok) {
		throw new Error("Failed to fetch events");
	}
	const data: OpenAgendaEditoResponse = await response.json();
	return data.events;
};

const EventComponent = React.memo(
	({
		event,
	}: {
		event: OpenAgendaEditoItem;
	}) => {
		const handleKeywordChange = useCallback(
			(_, newValue: string[]) => {
				const updatedEvent = {
					...event,
					keywords: newValue as string[],
					hasChanged: true,
				};
				console.log("Updated Event:", updatedEvent);
			},
			[event],
		);

		return (
			<div key={event.uid} className="">
				<h2 className="mb-0!">{event.title}</h2>
				<div>
					{event.nextTiming
						? DateTime.fromISO(event.nextTiming?.begin).toFormat(
								"ccc dd LLL HH:mm",
								{ locale: "fr-FR" },
							)
						: null}
				</div>
				<h3>⟜ {event.location.name}</h3>
				<div>
					{event.keywords?.map((keyword, index) => (
						<span key={`${event.uid}-keyword-${index}`}>{keyword} </span>
					))}
				</div>

				<Autocomplete
					className="w-full bg-white"
					multiple
					freeSolo
					id="notification_emails"
					options={[]}
					defaultValue={event.keywords || []}
					onChange={handleKeywordChange}
					renderTags={(value: readonly string[], getTagProps) =>
						value.map((option: string, index: number) => {
							const { key, ...tagProps } = getTagProps({ index });
							return (
								<Chip
									color="default"
									variant="filled"
									label={option}
									key={key}
									{...tagProps}
								/>
							);
						})
					}
					renderInput={(params) => <TextField {...params} />}
				/>
			</div>
		);
	},
);

const Edito = () => {
	const {
		data: events,
		isLoading,
		isError,
		refetch,
	} = useQuery({
		queryKey: ["editoEvents"],
		queryFn: fetchEditoEvents,
		enabled: false, // Disable automatic fetching
	});

	const handlePatch = async (eventDetails: OpenAgendaEditoItem) => {
		console.log("Event Details:", eventDetails.keywords);
		// Add any additional logic you need here
	};

	return (
		<div>
			<div className="flex items-center justify-center sticky top-0 z-[1000]">
				<button
					className="block cursor-pointer my-1 py-2 px-4 text-xl font-barlow uppercase text-teal bg-[#FFFFF0] border border-teal rounded-lg"
					type="button"
					onClick={() => refetch()}
					disabled={isLoading}
				>
					{isLoading ? (
						<ImSpinner7 className="animate-spin" />
					) : (
						"Charger les prochains événements de l'édito"
					)}
				</button>
			</div>
			<div className="grid grid-cols-4 gap-6">
				{isError ? (
					<p>Error loading events.</p>
				) : (
					events?.map((event) => (
						<div key={event.uid} className="">
							<h2 className="mb-0!">{event.title}</h2>
							<div>
								{event.nextTiming
									? DateTime.fromISO(event.nextTiming?.begin).toFormat(
											"ccc dd LLL HH:mm",
											{ locale: "fr-FR" },
										)
									: null}
							</div>
							<h3>⟜ {event.location.name}</h3>
							<div>
								{event.keywords?.map((keyword, index) => (
									<span key={`${event.uid}-keyword-${index}`}>{keyword} </span>
								))}
							</div>

							<EventComponent key={event.uid} event={event} />

							{/* <Autocomplete
								key={`${event.uid}-autocomplete`}
								className="w-full bg-white"
								multiple
								freeSolo
								id="notification_emails"
								options={[]}
								defaultValue={event.keywords || []}
								onChange={(_, newValue) => {
									console.log("new value", newValue);
									event.keywords = newValue as string[];
									event.hasChanged = true;
									console.log("event kw", event.keywords);
								}}
								renderTags={(value: readonly string[], getTagProps) => {
									console.log("value renderTags", value);
									return value.map((option: string, index: number) => {
										const { key, ...tagProps } = getTagProps({ index });
										return (
											<Chip
												color="default"
												variant="filled"
												label={option}
												key={key}
												{...tagProps}
											/>
										);
									});
								}}
								renderInput={(params) => {
									console.log("params renderInput", params);
									return <TextField {...params} />;
								}}
							/> */}

							<button
								className="block cursor-pointer my-1 py-2 px-4 text-xl font-barlow uppercase text-teal bg-[#FFFFF0] border border-teal rounded-lg"
								type="button"
								onClick={() => handlePatch(event)}
								disabled={isLoading}
							>
								{isLoading ? <ImSpinner7 className="animate-spin" /> : "Patch"}
							</button>
						</div>
					))
				)}
			</div>
		</div>
	);
};

export default Edito;
