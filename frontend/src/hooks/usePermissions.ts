import { useState, useCallback, useEffect } from 'react';

export type PermissionStatus = 'prompt' | 'granted' | 'denied' | 'unavailable';

export interface LocationCoordinates {
  latitude: number;
  longitude: number;
}

export const usePermissions = () => {
  const [cameraStatus, setCameraStatus] = useState<PermissionStatus>('prompt');
  const [locationStatus, setLocationStatus] = useState<PermissionStatus>('prompt');
  const [micStatus, setMicStatus] = useState<PermissionStatus>('prompt');
  const [coordinates, setCoordinates] = useState<LocationCoordinates | null>(null);

  const [isCameraRequesting, setIsCameraRequesting] = useState<boolean>(false);
  const [isMicRequesting, setIsMicRequesting] = useState<boolean>(false);

  // Check initial permissions if browser supports navigator.permissions
  useEffect(() => {
    if (typeof navigator !== 'undefined' && navigator.permissions?.query) {
      navigator.permissions
        .query({ name: 'geolocation' as PermissionName })
        .then((res) => {
          if (res.state === 'granted') setLocationStatus('granted');
          else if (res.state === 'denied') setLocationStatus('denied');
        })
        .catch(() => {});

      navigator.permissions
        .query({ name: 'camera' as any })
        .then((res) => {
          if (res.state === 'granted') setCameraStatus('granted');
          else if (res.state === 'denied') setCameraStatus('denied');
        })
        .catch(() => {});

      navigator.permissions
        .query({ name: 'microphone' as any })
        .then((res) => {
          if (res.state === 'granted') setMicStatus('granted');
          else if (res.state === 'denied') setMicStatus('denied');
        })
        .catch(() => {});
    }
  }, []);

  // Request Location
  const requestLocation = useCallback(async (): Promise<LocationCoordinates | null> => {
    if (!navigator.geolocation) {
      setLocationStatus('unavailable');
      return null;
    }
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const coords = {
            latitude: Number(pos.coords.latitude.toFixed(4)),
            longitude: Number(pos.coords.longitude.toFixed(4)),
          };
          setCoordinates(coords);
          setLocationStatus('granted');
          resolve(coords);
        },
        () => {
          setLocationStatus('denied');
          resolve(null);
        },
        { timeout: 8000, enableHighAccuracy: false }
      );
    });
  }, []);

  // Request Camera
  const requestCamera = useCallback(async (): Promise<boolean> => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraStatus('unavailable');
      return false;
    }
    setIsCameraRequesting(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      // Stop tracks immediately after permission check
      stream.getTracks().forEach((track) => track.stop());
      setCameraStatus('granted');
      return true;
    } catch {
      setCameraStatus('denied');
      return false;
    } finally {
      setIsCameraRequesting(false);
    }
  }, []);

  // Request Microphone
  const requestMicrophone = useCallback(async (): Promise<boolean> => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setMicStatus('unavailable');
      return false;
    }
    setIsMicRequesting(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      setMicStatus('granted');
      return true;
    } catch {
      setMicStatus('denied');
      return false;
    } finally {
      setIsMicRequesting(false);
    }
  }, []);

  return {
    cameraStatus,
    locationStatus,
    micStatus,
    coordinates,
    isCameraRequesting,
    isMicRequesting,
    requestLocation,
    requestCamera,
    requestMicrophone,
  };
};
