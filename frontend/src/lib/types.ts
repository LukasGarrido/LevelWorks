export interface Service {
    id: number;
    name: string;
    description: string | null;
    price: number;
    duration_minutes: number;
    photo: string | null;
}

export interface Slot {
    time: string;
    available: boolean;
}

export interface ReservationClientInfo {
    name: string;
    email: string;
    phone: string;
}

export interface ReservationPayload {
    client: ReservationClientInfo;
    service_id: number;
    scheduled_at: string; // ISO 8601 estándar internacional que establece un formato claro y sin ambigüedades para representar fechas y horas
    vehicle?: string;
    notes?: string;
}

export interface ReservationResponse {
    id: number;
    client_id: number;
    service_id: number;
    scheduled_at: string;
    status: string;
    vehicle: string | null;
    notes: string | null;
}