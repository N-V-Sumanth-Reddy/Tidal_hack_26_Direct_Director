'use client';

import { useState } from 'react';
import { Send, Plus, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Brief } from '@/lib/types';

interface BriefStepProps {
  brief?: Brief;
  onSubmit: (brief: Brief) => Promise<void>;
  isSubmitting?: boolean;
}

export function BriefStep({ brief, onSubmit, isSubmitting }: BriefStepProps) {
  const [formData, setFormData] = useState<Brief>(
    brief || {
      platform: 'YouTube',
      duration: 30,
      budget: 50000,
      location: 'Temple-like workshop, Urban coastline, Industrial foundry, Modern vault',
      constraints: ['Family friendly', 'No violence', 'Sustainable messaging', 'Premium aesthetics'],
      creativeDirection: 'Epic "Reverse Unboxing" concept - A phone that gives back to the planet. Show the journey of recycled materials (ocean-bound plastics, recycled aluminum, traceable metals) being transformed into a sustainable smartphone. Use reverse-time cinematography to show materials returning to their source, then being reborn as GreenPhone. Emphasize repairable design, modular components, and verified sustainable sourcing. Tone: Mythic, purposeful, premium. Visual style: Cinematic tech-fantasy with moody color palette (deep teal, warm gold light, charcoal shadows). Characters: ARJUN (28, principled protagonist) and MAYA (26, skeptical friend who becomes convinced). Key message: "In a world that only takes, hold the one that returns."',
      brandMandatories: ['GreenPhone', 'Green leaf logo', 'Traceable metals stamp', 'Modular design showcase'],
      targetAudience: 'Environmentally conscious millennials and Gen Z aged 25-35 who value sustainability, transparency, and premium design',
    }
  );

  const [newConstraint, setNewConstraint] = useState('');
  const [newMandatory, setNewMandatory] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.platform || !formData.creativeDirection || !formData.targetAudience) {
      alert('Please fill in all required fields');
      return;
    }

    await onSubmit(formData);
  };

  const addConstraint = () => {
    if (newConstraint.trim()) {
      setFormData({
        ...formData,
        constraints: [...formData.constraints, newConstraint.trim()],
      });
      setNewConstraint('');
    }
  };

  const removeConstraint = (index: number) => {
    setFormData({
      ...formData,
      constraints: formData.constraints.filter((_, i) => i !== index),
    });
  };

  const addMandatory = () => {
    if (newMandatory.trim()) {
      setFormData({
        ...formData,
        brandMandatories: [...formData.brandMandatories, newMandatory.trim()],
      });
      setNewMandatory('');
    }
  };

  const removeMandatory = (index: number) => {
    setFormData({
      ...formData,
      brandMandatories: formData.brandMandatories.filter((_, i) => i !== index),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Project Brief</h2>
        <p className="text-gray-600">
          Provide the details for your ad campaign. This information will guide the AI in
          generating concepts and screenplays.
        </p>
      </div>

      {/* Platform */}
      <div>
        <label htmlFor="platform" className="block text-sm font-medium text-gray-700 mb-2">
          Platform <span className="text-red-500">*</span>
        </label>
        <select
          id="platform"
          value={formData.platform}
          onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
          className={cn(
            'w-full px-4 py-2 rounded-lg border',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          )}
          required
        >
          <option value="">Select platform</option>
          <option value="YouTube">YouTube</option>
          <option value="Instagram">Instagram</option>
          <option value="TikTok">TikTok</option>
          <option value="Facebook">Facebook</option>
          <option value="TV">TV</option>
          <option value="Cinema">Cinema</option>
        </select>
      </div>

      {/* Duration and Budget */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
            Duration (seconds) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="duration"
            value={formData.duration}
            onChange={(e) =>
              setFormData({ ...formData, duration: parseInt(e.target.value) || 0 })
            }
            min="5"
            max="300"
            className={cn(
              'w-full px-4 py-2 rounded-lg border',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            )}
            required
          />
        </div>

        <div>
          <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-2">
            Budget ($) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="budget"
            value={formData.budget}
            onChange={(e) =>
              setFormData({ ...formData, budget: parseFloat(e.target.value) || 0 })
            }
            min="0"
            step="1000"
            className={cn(
              'w-full px-4 py-2 rounded-lg border',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            )}
            required
          />
        </div>
      </div>

      {/* Location */}
      <div>
        <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
          Location <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="location"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          placeholder="e.g., Urban, Studio, Beach, Office"
          className={cn(
            'w-full px-4 py-2 rounded-lg border',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          )}
          required
        />
      </div>

      {/* Creative Direction */}
      <div>
        <label
          htmlFor="creativeDirection"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Creative Direction <span className="text-red-500">*</span>
        </label>
        <textarea
          id="creativeDirection"
          value={formData.creativeDirection}
          onChange={(e) => setFormData({ ...formData, creativeDirection: e.target.value })}
          placeholder="Describe the creative vision, tone, style, and key message..."
          rows={4}
          className={cn(
            'w-full px-4 py-2 rounded-lg border resize-none',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          )}
          required
        />
      </div>

      {/* Target Audience */}
      <div>
        <label
          htmlFor="targetAudience"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Target Audience <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="targetAudience"
          value={formData.targetAudience}
          onChange={(e) => setFormData({ ...formData, targetAudience: e.target.value })}
          placeholder="e.g., Millennials, Tech enthusiasts, Parents"
          className={cn(
            'w-full px-4 py-2 rounded-lg border',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
          )}
          required
        />
      </div>

      {/* Constraints */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Constraints (Optional)
        </label>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={newConstraint}
            onChange={(e) => setNewConstraint(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addConstraint())}
            placeholder="Add a constraint..."
            className={cn(
              'flex-1 px-4 py-2 rounded-lg border',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            )}
          />
          <button
            type="button"
            onClick={addConstraint}
            className={cn(
              'px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200',
              'transition-colors'
            )}
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>
        {formData.constraints.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.constraints.map((constraint, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm"
              >
                {constraint}
                <button
                  type="button"
                  onClick={() => removeConstraint(index)}
                  className="hover:text-blue-900"
                >
                  <X className="h-4 w-4" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Brand Mandatories */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Brand Mandatories (Optional)
        </label>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={newMandatory}
            onChange={(e) => setNewMandatory(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMandatory())}
            placeholder="Add a brand mandatory..."
            className={cn(
              'flex-1 px-4 py-2 rounded-lg border',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            )}
          />
          <button
            type="button"
            onClick={addMandatory}
            className={cn(
              'px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200',
              'transition-colors'
            )}
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>
        {formData.brandMandatories.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {formData.brandMandatories.map((mandatory, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-100 text-purple-700 text-sm"
              >
                {mandatory}
                <button
                  type="button"
                  onClick={() => removeMandatory(index)}
                  className="hover:text-purple-900"
                >
                  <X className="h-4 w-4" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end pt-6 border-t">
        <button
          type="submit"
          disabled={isSubmitting}
          className={cn(
            'flex items-center gap-2 px-6 py-3 rounded-lg',
            'bg-blue-500 text-white font-medium',
            'hover:bg-blue-600 transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isSubmitting ? (
            <>
              <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              Submit Brief & Generate Concept
            </>
          )}
        </button>
      </div>
    </form>
  );
}
