import type { paths } from "./generated/openapi";
import { HttpClient, type SdkClientOptions } from "./runtime";

type LoginRequest = paths["/auth/login"]["post"]["requestBody"]["content"]["application/json"];
type LoginResponse = paths["/auth/login"]["post"]["responses"]["200"]["content"]["application/json"];
type RegisterRequest = paths["/auth/register"]["post"]["requestBody"]["content"]["application/json"];
type RegisterResponse = paths["/auth/register"]["post"]["responses"]["201"]["content"]["application/json"];
type MeResponse = paths["/auth/me"]["get"]["responses"]["200"]["content"]["application/json"];
type ListCoursesResponse = paths["/courses"]["get"]["responses"]["200"]["content"]["application/json"];
type QaRequest = paths["/courses/{course_id}/qa"]["post"]["requestBody"]["content"]["application/json"];
type QaResponse = paths["/courses/{course_id}/qa"]["post"]["responses"]["200"]["content"]["application/json"];
type ListDocumentsResponse = paths["/courses/{course_id}/documents"]["get"]["responses"]["200"]["content"]["application/json"];

export class AstraLearnSdk {
  private readonly http: HttpClient;

  constructor(options: SdkClientOptions) {
    this.http = new HttpClient(options);
  }

  setAccessToken(token: string | undefined): void {
    this.http.setAccessToken(token);
  }

  auth = {
    register: (payload: RegisterRequest): Promise<RegisterResponse> => {
      return this.http.post<RegisterRequest, RegisterResponse>("/auth/register", payload);
    },
    login: async (payload: LoginRequest): Promise<LoginResponse> => {
      const res = await this.http.post<LoginRequest, LoginResponse>("/auth/login", payload);
      this.http.setAccessToken(res.access_token);
      return res;
    },
    me: (): Promise<MeResponse> => {
      return this.http.get<MeResponse>("/auth/me");
    }
  };

  courses = {
    list: (): Promise<ListCoursesResponse> => {
      return this.http.get<ListCoursesResponse>("/courses");
    },
    qa: (courseId: string, payload: QaRequest): Promise<QaResponse> => {
      return this.http.post<QaRequest, QaResponse>(`/courses/${courseId}/qa`, payload);
    },
    listDocuments: (courseId: string): Promise<ListDocumentsResponse> => {
      return this.http.get<ListDocumentsResponse>(`/courses/${courseId}/documents`);
    }
  };
}
