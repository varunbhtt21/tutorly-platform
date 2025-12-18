/**
 * Portal Component
 *
 * Renders children into a DOM node that exists outside the DOM hierarchy
 * of the parent component. This is essential for modals, tooltips, and
 * dropdowns to ensure they render above all other content regardless of
 * parent z-index or overflow settings.
 *
 * Architecture Benefits:
 * - Modals are completely independent of parent component styling
 * - No z-index conflicts with navigation bars or other fixed elements
 * - Proper event bubbling isolation
 * - Accessibility improvements (focus trapping works correctly)
 */

import { useEffect, useState, ReactNode } from 'react';
import { createPortal } from 'react-dom';

interface PortalProps {
  children: ReactNode;
  containerId?: string;
}

/**
 * Portal renders its children into a separate DOM node.
 *
 * @param children - React nodes to render in the portal
 * @param containerId - DOM element ID to render into (defaults to 'modal-root')
 *
 * Usage:
 * ```tsx
 * <Portal>
 *   <div className="modal">Modal content</div>
 * </Portal>
 * ```
 */
export const Portal: React.FC<PortalProps> = ({
  children,
  containerId = 'modal-root'
}) => {
  const [mounted, setMounted] = useState(false);
  const [container, setContainer] = useState<HTMLElement | null>(null);

  useEffect(() => {
    // Find or create the container element
    let element = document.getElementById(containerId);

    if (!element) {
      // Create the container if it doesn't exist (fallback for SSR or missing setup)
      element = document.createElement('div');
      element.id = containerId;
      document.body.appendChild(element);
    }

    setContainer(element);
    setMounted(true);

    return () => {
      // Cleanup: only remove if we created it dynamically
      if (element && element.parentNode && !document.getElementById(containerId)) {
        element.parentNode.removeChild(element);
      }
    };
  }, [containerId]);

  // Don't render anything until mounted (prevents SSR hydration issues)
  if (!mounted || !container) {
    return null;
  }

  return createPortal(children, container);
};

export default Portal;
