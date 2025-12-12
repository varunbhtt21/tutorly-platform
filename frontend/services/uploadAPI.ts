/**
 * File Upload API Service
 *
 * Handles file uploads for:
 * - Profile photos
 * - Introduction videos
 * - Documents (certificates, diplomas)
 */

import apiClient from '../lib/axios';

// ============================================================================
// Types
// ============================================================================

export interface FileUploadResponse {
  id: string;
  user_id: string;
  original_filename: string;
  stored_filename: string;
  file_path: string;
  file_type: string;
  status: string;
  mime_type: string;
  file_size: number;
  public_url: string | null;
  thumbnail_url: string | null;
  is_optimized: boolean;
}

// ============================================================================
// Upload API
// ============================================================================

export const uploadAPI = {
  /**
   * Upload profile photo
   * @param file - Image file to upload
   * @param optimize - Whether to optimize the image (default: true)
   * @param createThumbnail - Whether to create thumbnail (default: true)
   */
  async uploadPhoto(
    file: File,
    optimize: boolean = true,
    createThumbnail: boolean = true
  ): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>(
      `/upload/photo?optimize=${optimize}&create_thumbnail_flag=${createThumbnail}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Upload introduction video
   * @param file - Video file to upload
   * @param generateThumbnail - Whether to generate video thumbnail (default: false)
   */
  async uploadVideo(
    file: File,
    generateThumbnail: boolean = false
  ): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>(
      `/upload/video?generate_thumbnail=${generateThumbnail}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Upload document (certificate, diploma, etc.)
   * @param file - Document file to upload
   * @param documentType - Type of document (default: 'certificate')
   */
  async uploadDocument(
    file: File,
    documentType: string = 'certificate'
  ): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>(
      `/upload/document?document_type=${documentType}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Delete uploaded file
   * @param fileId - ID of file to delete
   */
  async deleteFile(fileId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete(`/upload/${fileId}`);
    return response.data;
  },
};
