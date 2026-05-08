/**
 * Entity: Country
 * OOP wrapper around API country responses.
 */
export class Country {
  _id
  _name

  constructor(data = {}) {
    this._id = data.id ?? null
    this._name = data.name ?? ''
  }

  get id() { return this._id }
  get name() { return this._name }

  get displayName() {
    return this._name
      ? this._name.charAt(0).toUpperCase() + this._name.slice(1).toLowerCase()
      : ''
  }

  static fromAPI(data) {
    return new Country(data)
  }

  toPlainObject() {
    return { id: this._id, name: this._name }
  }
}

export default Country
