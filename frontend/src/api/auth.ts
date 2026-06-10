import client from "./client";
import type { AuthUser } from "../store/auth";

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const res = await client.post<LoginResponse>("/auth/login", {
    email,
    password,
  });
  return res.data;
}

export async function getMe(): Promise<AuthUser> {
  const res = await client.get<AuthUser>("/auth/me");
  return res.data;
}
