import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-brand-100 text-brand-800 dark:bg-brand-900 dark:text-brand-300",
        success: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300",
        warning: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300",
        danger: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
        secondary: "bg-[var(--muted)] text-[var(--muted-foreground)]",
        outline: "border border-[var(--border)] text-[var(--foreground)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
