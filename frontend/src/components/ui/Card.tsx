import { forwardRef } from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  footer?: React.ReactNode;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, title, description, footer, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'bg-white rounded-lg border border-gray-200 shadow-sm',
          className
        )}
        {...props}
      >
        {(title || description) && (
          <div className="px-6 py-4 border-b border-gray-200">
            {title && (
              <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            )}
            {description && (
              <p className="mt-1 text-sm text-gray-600">{description}</p>
            )}
          </div>
        )}
        
        <div className={clsx(
          !title && !description && 'p-6',
          (title || description) && !footer && 'p-6',
          (title || description) && footer && 'px-6 py-4'
        )}>
          {children}
        </div>
        
        {footer && (
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
            {footer}
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = 'Card';

export { Card };
