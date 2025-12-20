/**
 * DraggablePiP (Picture-in-Picture) Component
 *
 * A draggable container for the self-preview video in video calls.
 * Allows users to drag their self-view to any position within the viewport.
 *
 * Features:
 * - Drag to reposition anywhere on screen
 * - Snap to corners when released near edges
 * - Smooth animations
 * - Touch and mouse support
 * - Constrained within viewport bounds
 *
 * Architecture:
 * This is a presentation component that wraps any child content (typically VideoTile)
 * and adds drag functionality. It doesn't know about video-specific logic.
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Move } from 'lucide-react';

interface Position {
  x: number;
  y: number;
}

interface DraggablePiPProps {
  children: React.ReactNode;
  /** Initial corner position */
  initialPosition?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  /** Width of the PiP container */
  width?: string;
  /** Height of the PiP container */
  height?: string;
  /** Additional CSS classes */
  className?: string;
  /** Margin from viewport edges */
  edgeMargin?: number;
}

type Corner = 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';

export const DraggablePiP: React.FC<DraggablePiPProps> = ({
  children,
  initialPosition = 'bottom-right',
  width = 'w-48 lg:w-64',
  height = 'h-36 lg:h-48',
  className = '',
  edgeMargin = 16,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [corner, setCorner] = useState<Corner>(initialPosition);
  const dragStartRef = useRef<{ x: number; y: number; posX: number; posY: number } | null>(null);

  // Calculate position based on corner
  const getCornerPosition = useCallback((cornerPos: Corner): Position => {
    if (!containerRef.current) return { x: 0, y: 0 };

    const rect = containerRef.current.getBoundingClientRect();
    const parentRect = containerRef.current.parentElement?.getBoundingClientRect();

    if (!parentRect) return { x: 0, y: 0 };

    const maxX = parentRect.width - rect.width - edgeMargin;
    const maxY = parentRect.height - rect.height - edgeMargin;

    switch (cornerPos) {
      case 'bottom-right':
        return { x: maxX, y: maxY };
      case 'bottom-left':
        return { x: edgeMargin, y: maxY };
      case 'top-right':
        return { x: maxX, y: edgeMargin };
      case 'top-left':
        return { x: edgeMargin, y: edgeMargin };
      default:
        return { x: maxX, y: maxY };
    }
  }, [edgeMargin]);

  // Initialize position on mount and resize
  useEffect(() => {
    const updatePosition = () => {
      setPosition(getCornerPosition(corner));
    };

    // Initial position after render
    const timer = setTimeout(updatePosition, 100);

    // Update on resize
    window.addEventListener('resize', updatePosition);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', updatePosition);
    };
  }, [corner, getCornerPosition]);

  // Find nearest corner for snapping
  const findNearestCorner = useCallback((pos: Position): Corner => {
    if (!containerRef.current) return 'bottom-right';

    const rect = containerRef.current.getBoundingClientRect();
    const parentRect = containerRef.current.parentElement?.getBoundingClientRect();

    if (!parentRect) return 'bottom-right';

    const centerX = pos.x + rect.width / 2;
    const centerY = pos.y + rect.height / 2;

    const midX = parentRect.width / 2;
    const midY = parentRect.height / 2;

    const isRight = centerX > midX;
    const isBottom = centerY > midY;

    if (isBottom && isRight) return 'bottom-right';
    if (isBottom && !isRight) return 'bottom-left';
    if (!isBottom && isRight) return 'top-right';
    return 'top-left';
  }, []);

  // Constrain position within bounds
  const constrainPosition = useCallback((pos: Position): Position => {
    if (!containerRef.current) return pos;

    const rect = containerRef.current.getBoundingClientRect();
    const parentRect = containerRef.current.parentElement?.getBoundingClientRect();

    if (!parentRect) return pos;

    const maxX = parentRect.width - rect.width - edgeMargin;
    const maxY = parentRect.height - rect.height - edgeMargin;

    return {
      x: Math.max(edgeMargin, Math.min(pos.x, maxX)),
      y: Math.max(edgeMargin, Math.min(pos.y, maxY)),
    };
  }, [edgeMargin]);

  // Handle drag start
  const handleDragStart = useCallback((clientX: number, clientY: number) => {
    setIsDragging(true);
    dragStartRef.current = {
      x: clientX,
      y: clientY,
      posX: position.x,
      posY: position.y,
    };
  }, [position]);

  // Handle drag move
  const handleDragMove = useCallback((clientX: number, clientY: number) => {
    if (!isDragging || !dragStartRef.current) return;

    const deltaX = clientX - dragStartRef.current.x;
    const deltaY = clientY - dragStartRef.current.y;

    const newPosition = constrainPosition({
      x: dragStartRef.current.posX + deltaX,
      y: dragStartRef.current.posY + deltaY,
    });

    setPosition(newPosition);
  }, [isDragging, constrainPosition]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;

    setIsDragging(false);
    dragStartRef.current = null;

    // Snap to nearest corner
    const nearestCorner = findNearestCorner(position);
    setCorner(nearestCorner);
    setPosition(getCornerPosition(nearestCorner));
  }, [isDragging, position, findNearestCorner, getCornerPosition]);

  // Mouse event handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    handleDragStart(e.clientX, e.clientY);
  }, [handleDragStart]);

  // Touch event handlers
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    handleDragStart(touch.clientX, touch.clientY);
  }, [handleDragStart]);

  // Global mouse/touch move and up handlers
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      handleDragMove(e.clientX, e.clientY);
    };

    const handleMouseUp = () => {
      handleDragEnd();
    };

    const handleTouchMove = (e: TouchEvent) => {
      const touch = e.touches[0];
      handleDragMove(touch.clientX, touch.clientY);
    };

    const handleTouchEnd = () => {
      handleDragEnd();
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleTouchEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isDragging, handleDragMove, handleDragEnd]);

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      className={`
        absolute z-10 rounded-xl overflow-hidden shadow-2xl border-2 border-gray-700
        ${width} ${height}
        ${isDragging ? 'cursor-grabbing scale-105' : 'cursor-grab'}
        transition-shadow duration-200
        ${isDragging ? 'shadow-primary-500/30' : ''}
        ${className}
      `}
      style={{
        left: position.x,
        top: position.y,
        transition: isDragging ? 'none' : 'left 0.3s ease-out, top 0.3s ease-out, transform 0.2s ease-out',
        touchAction: 'none',
      }}
    >
      {/* Content */}
      {children}

      {/* Drag handle indicator */}
      <div
        className={`
          absolute top-2 left-1/2 -translate-x-1/2
          px-2 py-1 rounded-full bg-black/50 backdrop-blur-sm
          transition-opacity duration-200
          ${isDragging ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}
        `}
      >
        <Move size={12} className="text-white/70" />
      </div>

      {/* Hover/drag overlay */}
      <div
        className={`
          absolute inset-0 bg-primary-500/10 pointer-events-none
          transition-opacity duration-200
          ${isDragging ? 'opacity-100' : 'opacity-0'}
        `}
      />
    </div>
  );
};

export default DraggablePiP;
