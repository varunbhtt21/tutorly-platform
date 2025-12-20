/**
 * Popover Positioning Utility
 *
 * A reusable utility for calculating smart popover/modal positions that:
 * - Stay within viewport bounds
 * - Flip direction when there's not enough space
 * - Support configurable preferred placements
 * - Handle both container-relative and viewport-relative positioning
 *
 * Architecture:
 * - Pure functions for testability
 * - No side effects
 * - Configurable via options object
 * - Returns calculated position with metadata about adjustments made
 */

export type Placement = 'top' | 'bottom' | 'left' | 'right';
export type Alignment = 'start' | 'center' | 'end';

export interface PopoverDimensions {
  width: number;
  height: number;
}

export interface AnchorPoint {
  x: number;
  y: number;
}

export interface BoundingRect {
  top: number;
  left: number;
  right: number;
  bottom: number;
  width: number;
  height: number;
}

export interface PositionOptions {
  /** Preferred placement relative to anchor point */
  preferredPlacement?: Placement;
  /** Alignment along the placement axis */
  alignment?: Alignment;
  /** Margin from edges */
  margin?: number;
  /** Offset from anchor point */
  offset?: number;
  /** Whether to flip placement if not enough space */
  allowFlip?: boolean;
  /** Container bounds (defaults to viewport) */
  containerBounds?: BoundingRect;
}

export interface CalculatedPosition {
  top: number;
  left: number;
  /** The actual placement used (may differ from preferred if flipped) */
  actualPlacement: Placement;
  /** Whether the position was flipped from preferred */
  wasFlipped: boolean;
  /** Whether any adjustment was made */
  wasAdjusted: boolean;
}

const DEFAULT_OPTIONS: Required<PositionOptions> = {
  preferredPlacement: 'bottom',
  alignment: 'start',
  margin: 8,
  offset: 10,
  allowFlip: true,
  containerBounds: {
    top: 0,
    left: 0,
    right: typeof window !== 'undefined' ? window.innerWidth : 1920,
    bottom: typeof window !== 'undefined' ? window.innerHeight : 1080,
    width: typeof window !== 'undefined' ? window.innerWidth : 1920,
    height: typeof window !== 'undefined' ? window.innerHeight : 1080,
  },
};

/**
 * Get current viewport bounds
 */
export function getViewportBounds(): BoundingRect {
  if (typeof window === 'undefined') {
    return DEFAULT_OPTIONS.containerBounds;
  }
  return {
    top: 0,
    left: 0,
    right: window.innerWidth,
    bottom: window.innerHeight,
    width: window.innerWidth,
    height: window.innerHeight,
  };
}

/**
 * Check if a position fits within bounds
 */
function fitsInBounds(
  position: { top: number; left: number },
  dimensions: PopoverDimensions,
  bounds: BoundingRect,
  margin: number
): boolean {
  return (
    position.top >= bounds.top + margin &&
    position.left >= bounds.left + margin &&
    position.top + dimensions.height <= bounds.bottom - margin &&
    position.left + dimensions.width <= bounds.right - margin
  );
}

/**
 * Calculate position for a specific placement
 */
function calculatePositionForPlacement(
  anchor: AnchorPoint,
  dimensions: PopoverDimensions,
  placement: Placement,
  alignment: Alignment,
  offset: number
): { top: number; left: number } {
  let top = anchor.y;
  let left = anchor.x;

  // Calculate based on placement
  switch (placement) {
    case 'bottom':
      top = anchor.y + offset;
      break;
    case 'top':
      top = anchor.y - dimensions.height - offset;
      break;
    case 'right':
      left = anchor.x + offset;
      break;
    case 'left':
      left = anchor.x - dimensions.width - offset;
      break;
  }

  // Apply alignment for vertical placements
  if (placement === 'top' || placement === 'bottom') {
    switch (alignment) {
      case 'start':
        // left stays at anchor.x
        break;
      case 'center':
        left = anchor.x - dimensions.width / 2;
        break;
      case 'end':
        left = anchor.x - dimensions.width;
        break;
    }
  }

  // Apply alignment for horizontal placements
  if (placement === 'left' || placement === 'right') {
    switch (alignment) {
      case 'start':
        // top stays at anchor.y
        break;
      case 'center':
        top = anchor.y - dimensions.height / 2;
        break;
      case 'end':
        top = anchor.y - dimensions.height;
        break;
    }
  }

  return { top, left };
}

/**
 * Get the opposite placement for flipping
 */
function getOppositePlacement(placement: Placement): Placement {
  const opposites: Record<Placement, Placement> = {
    top: 'bottom',
    bottom: 'top',
    left: 'right',
    right: 'left',
  };
  return opposites[placement];
}

/**
 * Clamp a position to fit within bounds
 */
function clampToBounds(
  position: { top: number; left: number },
  dimensions: PopoverDimensions,
  bounds: BoundingRect,
  margin: number
): { top: number; left: number } {
  return {
    top: Math.max(
      bounds.top + margin,
      Math.min(position.top, bounds.bottom - dimensions.height - margin)
    ),
    left: Math.max(
      bounds.left + margin,
      Math.min(position.left, bounds.right - dimensions.width - margin)
    ),
  };
}

/**
 * Calculate the optimal position for a popover
 *
 * @param anchor - The point to position relative to (usually click coordinates)
 * @param dimensions - The width and height of the popover
 * @param options - Positioning options
 * @returns The calculated position with metadata
 *
 * @example
 * ```ts
 * const position = calculatePopoverPosition(
 *   { x: event.clientX, y: event.clientY },
 *   { width: 288, height: 280 },
 *   { preferredPlacement: 'bottom', margin: 10 }
 * );
 * ```
 */
export function calculatePopoverPosition(
  anchor: AnchorPoint,
  dimensions: PopoverDimensions,
  options: PositionOptions = {}
): CalculatedPosition {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const bounds = opts.containerBounds ?? getViewportBounds();

  // Try preferred placement
  let position = calculatePositionForPlacement(
    anchor,
    dimensions,
    opts.preferredPlacement,
    opts.alignment,
    opts.offset
  );

  let actualPlacement = opts.preferredPlacement;
  let wasFlipped = false;

  // Check if position fits, try flipping if allowed
  if (!fitsInBounds(position, dimensions, bounds, opts.margin)) {
    if (opts.allowFlip) {
      const oppositePlacement = getOppositePlacement(opts.preferredPlacement);
      const flippedPosition = calculatePositionForPlacement(
        anchor,
        dimensions,
        oppositePlacement,
        opts.alignment,
        opts.offset
      );

      if (fitsInBounds(flippedPosition, dimensions, bounds, opts.margin)) {
        position = flippedPosition;
        actualPlacement = oppositePlacement;
        wasFlipped = true;
      }
    }
  }

  // Final clamping to ensure it stays in bounds
  const originalPosition = { ...position };
  position = clampToBounds(position, dimensions, bounds, opts.margin);

  const wasAdjusted =
    wasFlipped ||
    position.top !== originalPosition.top ||
    position.left !== originalPosition.left;

  return {
    ...position,
    actualPlacement,
    wasFlipped,
    wasAdjusted,
  };
}

/**
 * Calculate popover position relative to a container element
 *
 * This is useful when the popover is positioned within a scrollable container
 * rather than the viewport.
 *
 * @param anchor - Click coordinates (client coordinates)
 * @param dimensions - Popover dimensions
 * @param containerRect - The container's bounding rect
 * @param options - Additional options
 * @returns Position relative to the container
 *
 * @example
 * ```ts
 * const gridRect = gridRef.current?.getBoundingClientRect();
 * const position = calculatePopoverPositionInContainer(
 *   { x: event.clientX, y: event.clientY },
 *   { width: 288, height: 280 },
 *   gridRect,
 *   { preferredPlacement: 'bottom' }
 * );
 * ```
 */
export function calculatePopoverPositionInContainer(
  anchor: AnchorPoint,
  dimensions: PopoverDimensions,
  containerRect: BoundingRect,
  options: Omit<PositionOptions, 'containerBounds'> = {}
): CalculatedPosition {
  // Convert anchor from viewport coordinates to container-relative coordinates
  const relativeAnchor: AnchorPoint = {
    x: anchor.x - containerRect.left,
    y: anchor.y - containerRect.top,
  };

  // Create container bounds in container-relative coordinates
  const containerBounds: BoundingRect = {
    top: 0,
    left: 0,
    right: containerRect.width,
    bottom: containerRect.height,
    width: containerRect.width,
    height: containerRect.height,
  };

  return calculatePopoverPosition(relativeAnchor, dimensions, {
    ...options,
    containerBounds,
  });
}
