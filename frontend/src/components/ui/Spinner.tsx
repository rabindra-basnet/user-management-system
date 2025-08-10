import { cva, type VariantProps } from 'class-variance-authority';
import { clsx } from 'clsx';

const spinnerVariants = cva(
  'animate-spin rounded-full border-2 border-gray-300',
  {
    variants: {
      size: {
        sm: 'h-4 w-4 border-t-gray-600',
        md: 'h-6 w-6 border-t-gray-600',
        lg: 'h-8 w-8 border-t-blue-600',
        xl: 'h-12 w-12 border-t-blue-600',
      },
      color: {
        primary: 'border-t-blue-600',
        secondary: 'border-t-gray-600',
        success: 'border-t-green-600',
        warning: 'border-t-yellow-600',
        error: 'border-t-red-600',
      },
    },
    defaultVariants: {
      size: 'md',
      color: 'primary',
    },
  }
);

export interface SpinnerProps extends VariantProps<typeof spinnerVariants> {
  className?: string;
}

export function Spinner({ size, color, className }: SpinnerProps) {
  return (
    <div className={clsx(spinnerVariants({ size, color }), className)} />
  );
}
