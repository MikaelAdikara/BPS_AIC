import {
  useEffect,
  useId,
  type ButtonHTMLAttributes,
  type HTMLAttributes,
  type InputHTMLAttributes,
  type ReactNode,
} from "react";
import {
  AlertCircle,
  CheckCircle,
  FlaskConical,
  Info,
  LoaderCircle,
  X,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { useI18n } from "@/lib/i18n";
export type Tone = "info" | "good" | "warn" | "alert" | "muted";
export function Button({
  variant = "primary",
  size,
  busy = false,
  children,
  className,
  disabled,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "outline" | "text" | "danger";
  size?: "sm" | "lg";
  busy?: boolean;
}) {
  return (
    <button
      {...props}
      type={props.type ?? "button"}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      className={cn(
        "btn",
        "btn--" + variant,
        size && "btn--" + size,
        className,
      )}
    >
      {busy && <LoaderCircle size={16} className="spinner" aria-hidden />}
      {children}
    </button>
  );
}
export function Chip({
  tone = "muted",
  synthetic = false,
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone; synthetic?: boolean }) {
  const { t } = useI18n();
  return (
    <span {...props} className={cn("chip", "tone-" + tone, props.className)}>
      {synthetic && <FlaskConical size={14} aria-hidden />}
      {synthetic ? t("common.synthetic") : children}
    </span>
  );
}
export function Card({
  title,
  lead,
  icon,
  action,
  children,
  ...props
}: Omit<HTMLAttributes<HTMLElement>, "title"> & {
  title?: ReactNode;
  lead?: ReactNode;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section {...props} className={cn("card", props.className)}>
      {title && (
        <header className="card__header">
          <div>
            <h2 className="card__title">
              {icon}
              {title}
            </h2>
            {lead && <p className="muted">{lead}</p>}
          </div>
          {action}
        </header>
      )}
      <div className="card__body">{children}</div>
    </section>
  );
}
export function Notice({
  tone = "info",
  action,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement> & { tone?: Tone; action?: ReactNode }) {
  const Icon =
    tone === "good"
      ? CheckCircle
      : tone === "warn" || tone === "alert"
        ? AlertCircle
        : Info;
  return (
    <div
      {...props}
      role={props.role ?? "status"}
      className={cn("notice", "tone-" + tone, props.className)}
    >
      <Icon size={18} aria-hidden />
      <div className="notice__body">{children}</div>
      {action}
    </div>
  );
}
export function Field({
  label,
  hint,
  error,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  hint?: string;
  error?: string;
}) {
  const generated = useId();
  const fieldId = id ?? generated;
  return (
    <div className="field">
      <label htmlFor={fieldId} className="field__label">
        {label}
      </label>
      <input
        {...props}
        id={fieldId}
        aria-invalid={Boolean(error)}
        aria-describedby={
          error ? fieldId + "-error" : hint ? fieldId + "-hint" : undefined
        }
      />
      {hint && (
        <p id={fieldId + "-hint"} className="field__hint">
          {hint}
        </p>
      )}
      {error && (
        <p id={fieldId + "-error"} className="field__error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
export function Skeleton({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return <div {...props} aria-hidden className={cn("skeleton", className)} />;
}
export function LoadingState() {
  const { t } = useI18n();
  return (
    <div role="status" className="stack">
      <span className="visually-hidden">{t("common.loading")}</span>
      <Skeleton />
      <Skeleton />
      <Skeleton />
    </div>
  );
}
export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <h2>{title}</h2>
      <p className="muted">{description}</p>
      {action}
    </div>
  );
}
export function Toast({
  children,
  onClose,
  tone = "good",
  duration = 5000,
}: {
  children: ReactNode;
  onClose: () => void;
  tone?: Tone;
  duration?: number;
}) {
  const { t } = useI18n();
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);
  return (
    <Notice
      tone={tone}
      className="toast"
      action={
        <Button variant="text" aria-label={t("common.close")} onClick={onClose}>
          <X size={16} aria-hidden />
        </Button>
      }
    >
      {children}
    </Notice>
  );
}
export function Table({
  children,
  ...props
}: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="table-scroll">
      <table {...props} className={cn("table", props.className)}>
        {children}
      </table>
    </div>
  );
}
export function Quote({
  text,
  rating,
  date,
  reviewId,
  variant,
}: {
  text: string;
  rating?: number | null;
  date?: string | null;
  reviewId: string;
  variant?: string;
}) {
  return (
    <blockquote className="quote">
      <p>“{text}”</p>
      <footer>
        {[reviewId, rating == null ? null : rating + " ★", variant, date]
          .filter(Boolean)
          .join(" · ")}
      </footer>
    </blockquote>
  );
}
export function Metric({
  value,
  label,
  hint,
}: {
  value: ReactNode;
  label: string;
  hint?: string;
}) {
  return (
    <div>
      <div className="metric__value">{value}</div>
      <div className="metric__label">{label}</div>
      {hint && <p className="metric__hint">{hint}</p>}
    </div>
  );
}
