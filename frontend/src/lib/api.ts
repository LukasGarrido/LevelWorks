const API_URL = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${API_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail ?? `Error ${res.status}`);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
}

export function getServices() {
    return request<import("./types").Service[]>("/services/");
}

export function getService(id: number) {
    return request<import("./types").Service>(`/services/${id}`);
}

export function createReservation(payload: import("./types").ReservationPayload) {
    return request<import("./types").ReservationResponse>("/reservations/", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}