import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { ApiError, request } from "./http.js";
export interface User {
  id: number;
  email: string;
  name: string;
  is_demo: boolean;
  phone: string;
  channels: string[];
  telegram_linked: boolean;
}
type ContextValue = {
  user: User | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  login: (email: string, password: string) => Promise<User>;
  register: (email: string, password: string, name: string) => Promise<User>;
  logout: () => Promise<void>;
  demo: () => Promise<User>;
};
const Context = createContext<ContextValue | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const revision = useRef(0);
  const refresh = useCallback(async () => {
    const current = ++revision.current;
    setLoading(true);
    setError(null);
    try {
      const next = await request("/auth/me");
      if (current === revision.current) setUser(next);
    } catch (e) {
      if (current === revision.current) {
        if (e instanceof ApiError && e.status === 401) setUser(null);
        else setError(e instanceof ApiError ? e.code : "request_failed");
      }
    } finally {
      if (current === revision.current) setLoading(false);
    }
  }, []);
  useEffect(() => {
    void refresh();
    return () => {
      revision.current++;
    };
  }, [refresh]);
  async function authenticate(path: string, body: Record<string, string>) {
    const next = await request(path, { method: "POST", body });
    revision.current++;
    setUser(next);
    setError(null);
    setLoading(false);
    return next as User;
  }
  return (
    <Context.Provider
      value={{
        user,
        loading,
        error,
        refresh,
        login: (email, password) =>
          authenticate("/auth/login", { email, password }),
        register: (email, password, name) =>
          authenticate("/auth/register", { email, password, name }),
        logout: async () => {
          await request("/auth/logout", { method: "POST" });
          revision.current++;
          setUser(null);
          setError(null);
        },
        demo: () =>
          authenticate("/auth/login", {
            email: import.meta.env.VITE_DEMO_EMAIL || "demo@deciqo.app",
            password: import.meta.env.VITE_DEMO_PASSWORD || "deciqo-demo",
          }),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useAuth() {
  const value = useContext(Context);
  if (!value) throw new Error("AuthProvider required");
  return value;
}
