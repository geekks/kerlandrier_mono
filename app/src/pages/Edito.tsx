import { API_URL, editoQuery, OA_SLUG } from "../config";
import { DateTime } from "luxon";
import "../layout.css";
import type { OpenAgendaEditoItem } from "../types/OpenAgenda";
import type React from "react";
import { useCallback } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import { Chip, Tooltip } from "@mui/material";
import Login from "../components/Login";
import { CgSpinner } from "react-icons/cg";

// react-query key for refetch management
const EVENTS_QUERY_KEY = "events";

// http GET request to get events used with react-query useQuery
const fetchEvents = async (): Promise<OpenAgendaEditoItem[]> => {
	const response = await fetch(editoQuery);
	const res = await response.json();
	return res.events;
};

// http PATCH request to update keywords for one event
const patchEvent = async ({
	id,
	keywords,
}: { id: string; keywords: string[] }) => {
	const response = await fetch(`${API_URL}/event/keywords`, {
		method: "PATCH",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${localStorage.getItem("access_token")}`,
		},
		body: JSON.stringify({ uid: id, keywords }),
	});

	if (!response.ok) {
		throw new Error("Network response was not ok");
	}

	return response.json();
};

// Card of one event
const EventCard = ({ event }: { event: OpenAgendaEditoItem }) => {
	// react-query hook to manipulate GET query data
	const queryClient = useQueryClient();

	// react-query hook to PATCH data
	const saveKeywordsMutation = useMutation({
		mutationFn: patchEvent,
		onSuccess: (updatedEvent) => {
			console.log("updatedEvent - ", updatedEvent);
			queryClient.setQueryData(
				[EVENTS_QUERY_KEY],
				(oldEvents: OpenAgendaEditoItem[]) =>
					oldEvents.map((event: OpenAgendaEditoItem) =>
						event.uid === updatedEvent.id ? updatedEvent : event,
					),
			);
		},
		onError: (error) => {
			console.log(error);
		},
	});

	// useCallback to avoid abusive re-render
	const handleKeywordChange = useCallback(
		(id: string, newKeywords: string[]) => {
			queryClient.setQueryData(
				[EVENTS_QUERY_KEY],
				(oldEvents: OpenAgendaEditoItem[]) =>
					oldEvents.map((event: OpenAgendaEditoItem) =>
						event.uid === id ? { ...event, keywords: newKeywords } : event,
					),
			);
			saveKeywordsMutation.reset();
		},
		[queryClient, saveKeywordsMutation],
	);

	// useCallback to avoird abusive re-render
	const handlePatchEvent = useCallback(
		(event: OpenAgendaEditoItem) => {
			if (event) {
				saveKeywordsMutation.mutate({
					id: event.uid,
					keywords: event.keywords,
				});
			}
		},
		[saveKeywordsMutation],
	);

	const oaLink = `https://openagenda.com/fr/${OA_SLUG}/contribute/event/${event.uid}`;

	return (
		<div className="flex flex-col justify-between">
			<Tooltip
				title={event.longDescription ?? event.description}
				disableInteractive
			>
				<a href={oaLink} tabIndex={-1}>
					<h2>{event.title}</h2>
				</a>
			</Tooltip>
			<div>
				{event.nextTiming
					? DateTime.fromISO(event.nextTiming?.begin).toFormat(
							"ccc dd LLL HH:mm",
							{ locale: "fr-FR" },
						)
					: null}
			</div>
			<h3 className="mb-2">⟜ {event.location.name}</h3>
			<Autocomplete
				multiple
				freeSolo
				options={[]}
				value={event.keywords ?? []}
				onChange={(_, value) => handleKeywordChange(event.uid, value)}
				renderInput={(params) => (
					<TextField
						{...params}
						sx={{
							"& .MuiOutlinedInput-root": {
								"& fieldset": {
									borderColor: "transparent",
								},
								"&:hover fieldset": {
									borderColor: "transparent",
								},
								"&.Mui-focused fieldset": {
									borderColor: "transparent",
								},
							},
							backgroundColor: "white",
							boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
							fontFamily: "Barlow Condensed !important",
						}}
					/>
				)}
				renderTags={(value, getTagProps) =>
					value.map((option, index) => {
						const { key, ...otherProps } = getTagProps({ index });
						return (
							<Chip
								key={key}
								label={option}
								{...otherProps}
								sx={{
									fontFamily: "Barlow Condensed",
									textTransform: "uppercase",
								}}
							/>
						);
					})
				}
			/>
			<div className="text-center">
				<button
					className="m-2 px-5 py-2 text-teal-500 border border-teal-500 rounded-sm h-10 font-bold uppercase focus:outline-none focus:ring-2 focus:ring-teal-500"
					onClick={() => handlePatchEvent(event)}
					type="button"
				>
					{saveKeywordsMutation.isPending ? (
						<CgSpinner className="animate-spin" />
					) : (
						"Save"
					)}
					{saveKeywordsMutation.data && " (OK)"}
				</button>
				{saveKeywordsMutation.isError ? (
					<>
						<div className="text-red-500 text-sm mt-2">
							{saveKeywordsMutation.error.message}
						</div>
						<div className="text-red-500 text-sm mt-2">
							You should probably login again
						</div>
						<div className="text-red-500 text-sm mt-2">Sorry about that</div>
						<div className="text-red-500 text-sm mt-2">Really sorry</div>
					</>
				) : null}
			</div>
		</div>
	);
};

const EventList: React.FC = () => {
	const { data: events = [] } = useQuery<OpenAgendaEditoItem[]>({
		queryKey: [EVENTS_QUERY_KEY],
		queryFn: fetchEvents,
		refetchInterval: false,
		refetchOnWindowFocus: false,
	});

	if (!events) {
		return <div>Loading...</div>;
	}

	return (
		<div className="text-center">
			<Login />
			<div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
				{events.map((event) => (
					<EventCard key={event.uid} event={event} />
				))}
			</div>
		</div>
	);
};

export default EventList;
