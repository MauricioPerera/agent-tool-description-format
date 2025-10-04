import Ajv, {JSONSchemaType} from 'ajv';
import addFormats from 'ajv-formats';
import { ArdfResource } from './types';
import { schemas } from './schemas';

const ajv = new Ajv({ allErrors: true, allowUnionTypes: true });
addFormats(ajv);

const basicValidator = ajv.compile<ArdfResource>(schemas.basic as JSONSchemaType<ArdfResource>);
const enhancedValidator = ajv.compile<ArdfResource>(schemas.enhanced as JSONSchemaType<ArdfResource>);

export type ValidationMode = 'auto' | 'basic' | 'enhanced';

export interface ValidationResult {
  valid: boolean;
  errors?: string[];
}

export const validateResource = (resource: ArdfResource, mode: ValidationMode = 'auto'): ValidationResult => {
  const schemaVersion = resource.schema_version ?? '1.0.0';
  const validator =
    mode === 'basic'
      ? basicValidator
      : mode === 'enhanced'
      ? enhancedValidator
      : schemaVersion.startsWith('2.')
      ? enhancedValidator
      : basicValidator;

  const valid = validator(resource);
  return {
    valid,
    errors: valid
      ? undefined
      : (validator.errors ?? []).map((err) => ${err.instancePath || '/'} ),
  };
};
