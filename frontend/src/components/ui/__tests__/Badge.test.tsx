import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from '../Badge';
import React from 'react';

describe('StatusBadge Component', () => {
  it('renders APPROVED status correctly', () => {
    render(<StatusBadge status="APPROVED" />);
    expect(screen.getByText('APPROVED')).toBeInTheDocument();
  });

  it('renders DENIED status correctly', () => {
    render(<StatusBadge status="DENIED" />);
    expect(screen.getByText('DENIED')).toBeInTheDocument();
  });

  it('renders PENDING status correctly', () => {
    render(<StatusBadge status="PENDING" />);
    expect(screen.getByText('PENDING')).toBeInTheDocument();
  });

  it('renders UNKNOWN status correctly', () => {
    render(<StatusBadge status="UNKNOWN" />);
    expect(screen.getByText('UNKNOWN')).toBeInTheDocument();
  });
});
