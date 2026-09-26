import {
  Component,
  Suspense,
  lazy,
  useEffect,
  useState,
  type ComponentType,
  type ReactNode,
} from "react";
import { AuthProvider, useAuth } from "@/api/auth";
import { WorkspaceProvider } from "@/api/workspace";
import { WorkspaceShell } from "@/components/WorkspaceShell";
import { OverviewScreen } from "@/screens/OverviewScreen";
import { IssuesScreen } from "@/screens/IssuesScreen";
import { ProductScreen } from "@/screens/ProductScreen";
import { ProductsScreen } from "@/screens/ProductsScreen";
import { SettingsScreen } from "@/screens/SettingsScreen";
import { I18nProvider, useI18n } from "@/lib/i18n";
import { ThemeProvider } from "@/lib/theme";
import { navigate, resolveRoute } from "@/lib/router.js";
import { Brand, LangToggle, ThemeToggle } from "@/components/Brand.jsx";
import {
  Button,
  Card,
  EmptyState,
  LoadingState,
  Notice,
} from "@/components/ui";
const publicModules = import.meta.glob(
  "./screens/{LandingScreen,LoginScreen}.tsx",
);
function publicScreen(name: string) {
  const key = "./screens/" + name + ".tsx";
  if (!publicModules[key]) return null;
  return lazy(async () => {
    const module = (await publicModules[key]()) as { default?: ComponentType };
    return { default: module.default ?? PublicUnavailable };
  });
}
const Landing = publicScreen("LandingScreen");
const Login = publicScreen("LoginScreen");
function PublicUnavailable() {
  const { t, localizeError } = useI18n();
  const { demo, user } = useAuth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  return (
    <>
      <h1>Deciqo</h1>
      <EmptyState
        title={t("common.unavailable")}
        description={t("common.unavailableHint")}
        action={
          user ? (
            <a className="btn btn--primary" href="#/app">
              {t("common.overview")}
            </a>
          ) : (
            <Button
              busy={busy}
              onClick={async () => {
                setBusy(true);
                setError(null);
                try {
                  await demo();
                  navigate("/app");
                } catch (e) {
                  setError((e as { code?: string }).code ?? "request_failed");
                } finally {
                  setBusy(false);
                }
              }}
            >
              {t("common.demo")}
            </Button>
          )
        }
      />
      {error && <Notice tone="alert">{localizeError(error)}</Notice>}
    </>
  );
}
function Frame({ children }: { children: ReactNode }) {
  return (
    <div className="bootstrap-page">
      <header>
        <Brand />
        <div className="utility-bar">
          <LangToggle />
          <ThemeToggle />
        </div>
      </header>
      <main className="stack">{children}</main>
    </div>
  );
}
function Routes() {
  const [route, setRoute] = useState(() => resolveRoute(window.location.hash));
  const { user, loading, error, refresh } = useAuth();
  const { t, localizeError } = useI18n();
  useEffect(() => {
    const update = () =>
      setRoute((previous) => resolveRoute(window.location.hash, previous));
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);
  useEffect(() => {
    if (!loading && !error) {
      if (route.protected && !user) navigate("/login");
      else if (user && (route.path === "/login" || route.path === "/register"))
        navigate("/app");
    }
  }, [route.path, route.protected, user, loading, error]);
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [route.path]);
  if (route.protected && (loading || (!user && !error)))
    return (
      <Frame>
        <LoadingState />
      </Frame>
    );
  if (route.protected && error)
    return (
      <Frame>
        <h1>{t("common.sessionError")}</h1>
        <Notice tone="alert">{localizeError(error)}</Notice>
        <Button onClick={() => void refresh()}>{t("common.retry")}</Button>
      </Frame>
    );
  if (!route.known)
    return (
      <Frame>
        <h1>{t("common.notFound")}</h1>
        <EmptyState
          title={t("common.notFound")}
          description={t("common.notFoundHint")}
          action={
            <a className="btn btn--primary" href="#/">
              {t("common.home")}
            </a>
          }
        />
      </Frame>
    );
  if (!route.protected) {
    const Screen = route.path === "/" ? Landing : Login;
    return Screen ? (
      <Suspense
        fallback={
          <Frame>
            <LoadingState />
          </Frame>
        }
      >
        <Screen />
      </Suspense>
    ) : (
      <Frame>
        <PublicUnavailable />
      </Frame>
    );
  }
  const labels: Record<string, string> = {
    "/app": "overview",
    "/app/issues": "issues",
    "/app/listings": "products",
    "/app/sources": "sources",
    "/app/alerts": "alerts",
    "/app/settings": "settings",
  };
  return (
    <WorkspaceProvider key={user?.id}>
      <WorkspaceShell path={route.path}>
        {route.path === "/app" ? (
          <OverviewScreen />
        ) : route.path === "/app/issues" ? (
          <IssuesScreen query={route.query} />
        ) : route.path === "/app/settings" ? (
          <SettingsScreen />
        ) : route.path === "/app/listings" ? (
          <ProductsScreen />
        ) : route.productId ? (
          <ProductScreen productId={route.productId} query={route.query} />
        ) : (
          <>
            <h1>{t("common." + (labels[route.path] ?? "products"))}</h1>
            <Card>
              <EmptyState
                title={t("common.unavailable")}
                description={t("common.unavailableHint")}
                action={
                  <a className="btn btn--outline" href="#/app/issues">
                    {t("workspace.backIssues")}
                  </a>
                }
              />
            </Card>
          </>
        )}
      </WorkspaceShell>
    </WorkspaceProvider>
  );
}
class Boundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}
function Application() {
  const { t } = useI18n();
  return (
    <Boundary
      fallback={
        <Frame>
          <h1>{t("common.unknownError")}</h1>
          <Button onClick={() => window.location.reload()}>
            {t("common.retry")}
          </Button>
        </Frame>
      }
    >
      <Routes />
    </Boundary>
  );
}
export default function App() {
  return (
    <I18nProvider>
      <ThemeProvider>
        <AuthProvider>
          <Application />
        </AuthProvider>
      </ThemeProvider>
    </I18nProvider>
  );
}
