/**
 * Entity: User
 * OOP wrapper around API user responses with computed getters and business methods.
 */
export class User {
  constructor(data = {}) {
    this._id = data.id ?? null
    this._firstName = data.first_name ?? ''
    this._lastName = data.last_name ?? ''
    this._email = data.email ?? ''
    this._image = data.image ?? null
    this._phoneNumber = data.phone_number ?? null
    this._gender = data.gender ?? null
    this._dob = data.dob ?? null
    this._countryId = data.country_id ?? null
    this._mainLang = data.main_lang ?? null
    this._addLang = data.add_lang ?? null
    this._ethnicGroup = data.ethnic_group ?? null
    this._special = data.special ?? null
    this._roleType = data.role_type ?? 1
    this._insertDate = data.insert_date ?? null
    this._updateDate = data.update_date ?? null
    this._emailVerified = data.email_verified ?? false
  }

  // Getters
  get id() { return this._id }
  get firstName() { return this._firstName }
  get lastName() { return this._lastName }
  get email() { return this._email }
  get image() { return this._image }
  get phoneNumber() { return this._phoneNumber }
  get gender() { return this._gender }
  get dob() { return this._dob }
  get countryId() { return this._countryId }
  get mainLang() { return this._mainLang }
  get addLang() { return this._addLang }
  get ethnicGroup() { return this._ethnicGroup }
  get special() { return this._special }
  get roleType() { return this._roleType }
  get insertDate() { return this._insertDate }
  get updateDate() { return this._updateDate }
  get emailVerified() { return this._emailVerified }

  // Business methods
  get fullName() {
    return `${this._firstName} ${this._lastName}`.trim()
  }

  get displayAvatar() {
    return this._image || '/assets/default-avatar.png'
  }

  get isAdmin() {
    return this._roleType === 2
  }

  get isEmailVerified() {
    return this._emailVerified === true || this._emailVerified === 1
  }

  getPersonalInfo() {
    return {
      id: this._id,
      fullName: this.fullName,
      email: this._email,
      phoneNumber: this._phoneNumber,
      gender: this._gender,
      dob: this._dob,
      countryId: this._countryId,
      mainLang: this._mainLang,
      addLang: this._addLang,
      ethnicGroup: this._ethnicGroup,
      special: this._special,
      image: this._image,
    }
  }

  /**
   * Factory: create a User entity from a raw API response object.
   * @param {Object} data
   * @returns {User}
   */
  static fromAPI(data) {
    return new User(data)
  }

  /**
   * Serialize back to a plain object (for Pinia state persistence etc.)
   * @returns {Object}
   */
  toPlainObject() {
    return {
      id: this._id,
      first_name: this._firstName,
      last_name: this._lastName,
      email: this._email,
      image: this._image,
      phone_number: this._phoneNumber,
      gender: this._gender,
      dob: this._dob,
      country_id: this._countryId,
      main_lang: this._mainLang,
      add_lang: this._addLang,
      ethnic_group: this._ethnicGroup,
      special: this._special,
      role_type: this._roleType,
      insert_date: this._insertDate,
      update_date: this._updateDate,
      email_verified: this._emailVerified,
    }
  }
}

export default User
