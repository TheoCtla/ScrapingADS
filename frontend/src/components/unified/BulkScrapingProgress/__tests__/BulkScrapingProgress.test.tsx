import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import BulkScrapingProgress from '../BulkScrapingProgress';

describe('BulkScrapingProgress', () => {
  const defaultProps = {
    isVisible: true,
    currentClient: 'Test Client',
    currentIndex: 2,
    totalClients: 5,
    isProcessing: true,
    onCancel: jest.fn(),
    completedClients: ['Client 1', 'Client 2'],
    failedClients: [{ client: 'Client 3', error: 'Test error' }]
  };

  it('renders when visible', () => {
    render(<BulkScrapingProgress {...defaultProps} />);
    expect(screen.getByText('Scraping en masse des clients')).toBeInTheDocument();
  });

  it('does not render when not visible', () => {
    render(<BulkScrapingProgress {...defaultProps} isVisible={false} />);
    expect(screen.queryByText('Scraping en masse des clients')).not.toBeInTheDocument();
  });

  it('displays progress statistics', () => {
    render(<BulkScrapingProgress {...defaultProps} />);
    expect(screen.getByText('2 / 5')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Success count
    expect(screen.getByText('1')).toBeInTheDocument(); // Error count
  });

  it('shows current client when processing', () => {
    render(<BulkScrapingProgress {...defaultProps} />);
    expect(screen.getByText('Test Client')).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', () => {
    const onCancel = jest.fn();
    render(<BulkScrapingProgress {...defaultProps} onCancel={onCancel} />);
    
    fireEvent.click(screen.getByText('Annuler'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('disables cancel button when not processing', () => {
    render(<BulkScrapingProgress {...defaultProps} isProcessing={false} />);
    const cancelButton = screen.getByText('Annuler');
    expect(cancelButton).toBeDisabled();
  });

  it('shows completion summary when processing is complete', () => {
    render(<BulkScrapingProgress {...defaultProps} isProcessing={false} currentIndex={5} />);
    expect(screen.getByText('Résumé du traitement')).toBeInTheDocument();
    expect(screen.getByText('✅ Succès: 2')).toBeInTheDocument();
    expect(screen.getByText('❌ Échecs: 1')).toBeInTheDocument();
  });

  it('shows failed clients list when there are failures', () => {
    render(<BulkScrapingProgress {...defaultProps} isProcessing={false} currentIndex={5} />);
    expect(screen.getByText('Clients en échec:')).toBeInTheDocument();
    expect(screen.getByText('Client 3: Test error')).toBeInTheDocument();
  });
});
