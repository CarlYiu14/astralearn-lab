export type FetchLike = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

export type SdkClientOptions = {
  baseUrl: string;
  fetchImpl?: FetchLike;
  accessToken?: string;
};

export class SdkError extends Error {
  status: number;
  bodyText: string;

  constructor(status: number, bodyText: string) {
    super(`AstraLearn SDK request failed (${status})`);
    this.name = "SdkError";
    this.status = status;
    this.bodyText = bodyText;
  }
}

export class HttpClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: FetchLike;
  private accessToken?: string;

  constructor(opts: SdkClientOptions) {
    this.baseUrl = opts.baseUrl.replace(/\/+$/, "");
    this.fetchImpl = opts.fetchImpl ?? fetch;
    this.accessToken = opts.accessToken;
  }

  setAccessToken(token: string | undefined): void {
    this.accessToken = token;
  }

  async get<TResponse>(path: string): Promise<TResponse> {
    return this.request<void, TResponse>("GET", path, undefined);
  }

  async post<TRequest, TResponse>(path: string, body: TRequest): Promise<TResponse> {
    return this.request<TRequest, TResponse>("POST", path, body);
  }

  private async request<TRequest, TResponse>(
    method: "GET" | "POST",
    path: string,
    body: TRequest | undefined
  ): Promise<TResponse> {
    const headers: Record<string, string> = {
      Accept: "application/json"
    };
    if (this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }
    const hasBody = body !== undefined;
    if (hasBody) {
      headers["Content-Type"] = "application/json";
    }
    const res = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: hasBody ? JSON.stringify(body) : undefined
    });
    if (!res.ok) {
      throw new SdkError(res.status, await res.text());
    }
    return (await res.json()) as TResponse;
  }
}
