"use client";

import React from "react";

/**
 * Micro-interaction wrapper components for common patterns
 */

/**
 * Animated button with multiple states (hover, active, loading)
 */
export interface AnimatedButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export function AnimatedButton({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  children,
  disabled,
  ...props
}: AnimatedButtonProps) {
  const baseClasses =
    "inline-flex items-center justify-center gap-2 font-semibold transition-all duration-300 transform disabled:cursor-not-allowed";

  const sizeClasses = {
    sm: "px-3 py-2 text-sm rounded-lg",
    md: "px-6 py-3 text-base rounded-lg",
    lg: "px-8 py-4 text-lg rounded-xl",
  };

  const variantClasses = {
    primary:
      "bg-gradient-to-r from-primary-600 to-secondary-600 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 disabled:bg-neutral-300 disabled:shadow-none",
    secondary:
      "border-2 border-primary-600 text-primary-600 hover:bg-primary-50 hover:shadow-md active:scale-95 disabled:border-neutral-300 disabled:text-neutral-400",
    danger:
      "bg-red-600 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 disabled:bg-red-300",
    ghost:
      "text-neutral-700 hover:text-primary-600 hover:bg-neutral-50 active:scale-95 disabled:text-neutral-400",
  };

  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]}`}
      {...props}
    >
      {loading ? (
        <>
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span>Обработка...</span>
        </>
      ) : (
        <>
          {icon && <span>{icon}</span>}
          {children}
        </>
      )}
    </button>
  );
}

/**
 * Hover-lift card component
 */
export interface HoverLiftCardProps
  extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  interactive?: boolean;
}

export function HoverLiftCard({
  children,
  interactive = true,
  ...props
}: HoverLiftCardProps) {
  return (
    <div
      className={`
        rounded-xl bg-white border border-neutral-200 p-6 shadow-md
        transition-all duration-300 transform
        ${
          interactive
            ? "hover:shadow-xl hover:-translate-y-2 cursor-pointer active:scale-98"
            : ""
        }
      `}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Animated badge with different states
 */
export interface AnimatedBadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "success" | "warning" | "error" | "info";
  children: React.ReactNode;
}

export function AnimatedBadge({
  variant = "info",
  children,
  ...props
}: AnimatedBadgeProps) {
  const variantClasses = {
    success: "bg-green-100 text-green-700 border border-green-300",
    warning: "bg-amber-100 text-amber-700 border border-amber-300",
    error: "bg-red-100 text-red-700 border border-red-300",
    info: "bg-blue-100 text-blue-700 border border-blue-300",
  };

  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-semibold
        animate-fade-in ${variantClasses[variant]}
      `}
      {...props}
    >
      <span>
        {variant === "success" && "✓"}
        {variant === "warning" && "⚠"}
        {variant === "error" && "✕"}
        {variant === "info" && "ℹ"}
      </span>
      {children}
    </div>
  );
}

/**
 * Input with animated label and validation indicators
 */
export interface AnimatedInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: boolean;
  icon?: React.ReactNode;
}

export function AnimatedInput({
  label,
  error,
  success,
  icon,
  ...props
}: AnimatedInputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
          {label}
          {props.required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        <input
          className={`
            w-full px-4 py-3 rounded-lg border-2 outline-none transition-all duration-300
            placeholder:text-neutral-400 text-base text-neutral-900
            ${
              error
                ? "border-red-500 focus:ring-2 focus:ring-red-100 focus:border-red-600"
                : success
                ? "border-green-500 focus:ring-2 focus:ring-green-100 focus:border-green-600"
                : "border-neutral-200 hover:border-neutral-300 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 focus:shadow-lg"
            }
          `}
          {...props}
        />
        {icon && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xl">
            {icon}
          </span>
        )}
        {success && !error && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-green-500">
            ✓
          </span>
        )}
      </div>
      {error && (
        <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1 animate-fade-in">
          <span>✕</span> {error}
        </p>
      )}
      {success && !error && (
        <p className="mt-1.5 text-xs text-green-600 flex items-center gap-1 animate-fade-in">
          <span>✓</span> Готово!
        </p>
      )}
    </div>
  );
}

/**
 * Smooth collapse/expand animation
 */
export interface AnimatedCollapseProps {
  isOpen: boolean;
  children: React.ReactNode;
}

export function AnimatedCollapse({
  isOpen,
  children,
}: AnimatedCollapseProps) {
  return (
    <div
      className={`
        overflow-hidden transition-all duration-300 ease-out
        ${isOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0"}
      `}
    >
      {children}
    </div>
  );
}

/**
 * Loading spinner with multiple states
 */
export interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  color?: "primary" | "white" | "gray";
  text?: string;
}

export function LoadingSpinner({
  size = "md",
  color = "primary",
  text,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4 border",
    md: "h-8 w-8 border-2",
    lg: "h-12 w-12 border-4",
  };

  const colorClasses = {
    primary: "border-primary-600 border-t-transparent",
    white: "border-white border-t-transparent",
    gray: "border-neutral-300 border-t-transparent",
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`
          rounded-full animate-spin
          ${sizeClasses[size]} ${colorClasses[color]}
        `}
      />
      {text && (
        <p className="text-sm font-medium text-neutral-600">{text}</p>
      )}
    </div>
  );
}

/**
 * Toast notification (can be used with context for global notifications)
 */
export interface ToastProps {
  message: string;
  type?: "success" | "error" | "warning" | "info";
  duration?: number;
  onClose?: () => void;
}

export function Toast({ message, type = "info", onClose }: ToastProps) {
  React.useEffect(() => {
    const timer = setTimeout(() => onClose?.(), 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const typeClasses = {
    success:
      "bg-green-50 border border-green-200 text-green-800 before:content-['✓']",
    error:
      "bg-red-50 border border-red-200 text-red-800 before:content-['✕']",
    warning:
      "bg-amber-50 border border-amber-200 text-amber-800 before:content-['⚠']",
    info: "bg-blue-50 border border-blue-200 text-blue-800 before:content-['ℹ']",
  };

  return (
    <div
      className={`
        fixed bottom-4 right-4 rounded-lg px-4 py-3 shadow-lg
        animate-fade-in before:mr-2 before:font-bold
        ${typeClasses[type]}
      `}
    >
      {message}
    </div>
  );
}
