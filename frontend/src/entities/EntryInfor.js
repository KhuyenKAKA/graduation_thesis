/**
 * Entity: EntryInfor
 * OOP wrapper around entry requirement responses.
 */
export class EntryInfor {
  static DEGREE_BACHELOR = 1
  static DEGREE_MASTER = 2

  _id
  _universityId
  _degreeType
  _sat
  _gre
  _gmat
  _act
  _atar
  _gpa
  _toefl
  _ielts

  constructor(data = {}) {
    this._id = data.id ?? null
    this._universityId = data.university_id ?? null
    this._degreeType = data.degree_type ?? null
    this._sat = data.sat ?? null
    this._gre = data.gre ?? null
    this._gmat = data.gmat ?? null
    this._act = data.act ?? null
    this._atar = data.atar ?? null
    this._gpa = data.gpa ?? null
    this._toefl = data.toefl ?? null
    this._ielts = data.ielts ?? null
  }

  get id() { return this._id }
  get universityId() { return this._universityId }
  get degreeType() { return this._degreeType }
  get sat() { return this._sat }
  get gre() { return this._gre }
  get gmat() { return this._gmat }
  get act() { return this._act }
  get atar() { return this._atar }
  get gpa() { return this._gpa }
  get toefl() { return this._toefl }
  get ielts() { return this._ielts }

  get degreeLabel() {
    if (this._degreeType === EntryInfor.DEGREE_BACHELOR) return 'Bachelor'
    if (this._degreeType === EntryInfor.DEGREE_MASTER) return 'Master'
    return 'Unknown'
  }

  get isBachelor() { return this._degreeType === EntryInfor.DEGREE_BACHELOR }
  get isMaster() { return this._degreeType === EntryInfor.DEGREE_MASTER }

  getRequirementCards() {
    const cards = []
    const fields = [
      { label: 'SAT', value: this._sat },
      { label: 'GRE', value: this._gre },
      { label: 'GMAT', value: this._gmat },
      { label: 'ACT', value: this._act },
      { label: 'ATAR', value: this._atar },
      { label: 'GPA', value: this._gpa },
      { label: 'TOEFL', value: this._toefl },
      { label: 'IELTS', value: this._ielts },
    ]
    for (const f of fields) {
      if (f.value !== null && f.value !== undefined) {
        cards.push(f)
      }
    }
    return cards
  }

  get hasRequirements() {
    return this.getRequirementCards().length > 0
  }

  static fromAPI(data) {
    return new EntryInfor(data)
  }

  toPlainObject() {
    return {
      id: this._id,
      university_id: this._universityId,
      degree_type: this._degreeType,
      sat: this._sat,
      gre: this._gre,
      gmat: this._gmat,
      act: this._act,
      atar: this._atar,
      gpa: this._gpa,
      toefl: this._toefl,
      ielts: this._ielts,
    }
  }
}

export default EntryInfor
