/**
 * Entity: University
 * OOP wrapper around API university responses with computed getters and business methods.
 */
export class University {
  _id
  _name
  _region
  _regionId
  _countryId
  _city
  _logo
  _overallScore
  _rankInt
  _path
  _countryName
  _scores

  constructor(data = {}) {
    this._id = data.id ?? null
    this._name = data.name ?? ''
    this._region = data.region ?? null
    this._regionId = data.region_id ?? null
    this._countryId = data.country_id ?? null
    this._city = data.city ?? null
    this._logo = data.logo ?? null
    this._overallScore = data.overall_score ?? null
    this._rankInt = data.rank_int ?? data.rank ?? null
    this._path = data.path ?? null
    this._countryName = data.country_name ?? data.country ?? null
    this._scores = data.scores ?? {}
  }

  // Getters
  get id() { return this._id }
  get name() { return this._name }
  get region() { return this._region }
  get regionId() { return this._regionId }
  get countryId() { return this._countryId }
  get city() { return this._city }
  get logo() { return this._logo }
  get overallScore() { return this._overallScore }
  get rankInt() { return this._rankInt }
  get path() { return this._path }
  get countryName() { return this._countryName }
  get scores() { return this._scores }

  // Business methods
  get displayRank() {
    if (this._rankInt === null || this._rankInt === undefined) return 'N/A'
    return `#${this._rankInt}`
  }

  get formattedScore() {
    if (this._overallScore === null || this._overallScore === undefined) return 'N/A'
    return Number(this._overallScore).toFixed(1)
  }

  get hasLogo() {
    return Boolean(this._logo)
  }

  get hasScores() {
    return Object.keys(this._scores).length > 0
  }

  get location() {
    const parts = [this._city, this._countryName].filter(Boolean)
    return parts.length ? parts.join(', ') : ''
  }

  /**
   * Factory: create a University entity from a raw API response object.
   * @param {Object} data
   * @returns {University}
   */
  static fromAPI(data) {
    return new University(data)
  }

  /**
   * Serialize back to a plain object.
   * @returns {Object}
   */
  toPlainObject() {
    return {
      id: this._id,
      name: this._name,
      region: this._region,
      region_id: this._regionId,
      country_id: this._countryId,
      city: this._city,
      logo: this._logo,
      overall_score: this._overallScore,
      rank_int: this._rankInt,
      rank: this._rankInt,
      path: this._path,
      country_name: this._countryName,
      country: this._countryName,
      scores: this._scores,
    }
  }
}

export default University
