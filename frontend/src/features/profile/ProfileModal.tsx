import React, { useState, useEffect } from 'react';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { useAuthStore } from '../../stores/authStore';
import { profileService } from '../../services/profileService';
import { SUPPORTED_LANGUAGES } from '../../stores/languageStore';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose }) => {
  const { user, setProfile } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);

  const [language, setLanguage] = useState('en');
  const [state, setState] = useState('');
  const [district, setDistrict] = useState('');
  const [village, setVillage] = useState('');
  const [landSize, setLandSize] = useState('');
  const [soilType, setSoilType] = useState('Loamy Soil');
  const [irrigation, setIrrigation] = useState('Canal');

  useEffect(() => {
    if (user?.profile) {
      setLanguage(user.profile.preferred_language || 'en');
      setState(user.profile.state || '');
      setDistrict(user.profile.district || '');
      setVillage(user.profile.village || '');
      setLandSize(user.profile.land_size_acres ? String(user.profile.land_size_acres) : '');
      setSoilType(user.profile.soil_type || 'Loamy Soil');
      setIrrigation(user.profile.irrigation_source || 'Canal');
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setSuccessMsg(false);
    try {
      const updated = await profileService.updateProfile({
        preferred_language: language,
        state: state || undefined,
        district: district || undefined,
        village: village || undefined,
        land_size_acres: landSize ? parseFloat(landSize) : undefined,
        soil_type: soilType,
        irrigation_source: irrigation,
      });
      setProfile(updated);
      setSuccessMsg(true);
      setTimeout(() => {
        setSuccessMsg(false);
        onClose();
      }, 1200);
    } catch {
      // Error handled
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Farmer & Land Profile">
      {successMsg && (
        <div
          style={{
            backgroundColor: 'var(--color-success-bg)',
            color: 'var(--color-success)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: 'var(--font-size-sm)',
            marginBottom: '1rem',
            fontWeight: 600,
          }}
        >
          Farm profile updated successfully!
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <Input
            label="State"
            placeholder="e.g. Punjab"
            value={state}
            onChange={(e) => setState(e.target.value)}
            leftIcon={<span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--color-text-tertiary)' }}>location_on</span>}
          />
          <Input
            label="District"
            placeholder="e.g. Ludhiana"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          />
        </div>

        <Input
          label="Village / Tehsil"
          placeholder="e.g. Sahnewal"
          value={village}
          onChange={(e) => setVillage(e.target.value)}
        />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <Input
            label="Total Land Size (Acres)"
            type="number"
            step="0.1"
            placeholder="e.g. 5.5"
            value={landSize}
            onChange={(e) => setLandSize(e.target.value)}
          />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Primary Soil Type
            </label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              style={{
                width: '100%',
                minHeight: '48px',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                border: '1.5px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                fontSize: 'var(--font-size-base)',
                color: 'var(--color-text-primary)',
                outline: 'none',
              }}
            >
              <option value="Alluvial Soil">Alluvial Soil</option>
              <option value="Black Soil">Black / Regur Soil</option>
              <option value="Red Soil">Red Soil</option>
              <option value="Laterite Soil">Laterite Soil</option>
              <option value="Sandy Loam">Sandy Loam</option>
              <option value="Clay Loam">Clay Loam</option>
              <option value="Loamy Soil">Loamy Soil</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Irrigation Source
            </label>
            <select
              value={irrigation}
              onChange={(e) => setIrrigation(e.target.value)}
              style={{
                width: '100%',
                minHeight: '48px',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                border: '1.5px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                fontSize: 'var(--font-size-base)',
                color: 'var(--color-text-primary)',
                outline: 'none',
              }}
            >
              <option value="Canal">Canal Irrigation</option>
              <option value="Tube Well">Tube Well / Borewell</option>
              <option value="Drip Irrigation">Drip / Micro-irrigation</option>
              <option value="Rainfed">Rainfed (Monsoon)</option>
              <option value="Pond / Tank">Pond / Tank</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <label style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--color-text-primary)' }}>
              Preferred Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{
                width: '100%',
                minHeight: '48px',
                padding: '0.65rem 0.85rem',
                borderRadius: 'var(--radius-md)',
                border: '1.5px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                fontSize: 'var(--font-size-base)',
                color: 'var(--color-text-primary)',
                outline: 'none',
              }}
            >
              {SUPPORTED_LANGUAGES.map((l: any) => (
                <option key={l.code} value={l.code}>
                  {l.nativeName} ({l.name})
                </option>
              ))}
            </select>
          </div>
        </div>

        <Button type="submit" isLoading={isLoading} fullWidth style={{ marginTop: '0.5rem' }}>
          Save Farm Details
        </Button>
      </form>
    </Modal>
  );
};
