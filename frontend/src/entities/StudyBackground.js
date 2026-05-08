/**
 * Entity: StudyBackground
 * OOP wrapper around API study_bg responses.
 */
export class StudyBackground {
  _id
  _userId
  _level
  _major
  _academicRate
  _gpa
  _graduateYear
  _act
  _gmat
  _sat
  _cat
  _gre
  _stat
  _ielts
  _toefl
  _pearsonTest
  _camAdvTest
  _interBac

  constructor(data = {}) {
    this._id = data.id ?? null
    this._userId = data.user_id ?? null
    this._level = data.level ?? null
    this._major = data.major ?? null
    this._academicRate = data.academic_rate ?? null
    this._gpa = data.gpa ?? null
    this._graduateYear = data.graduate_year ?? null
    this._act = data.act ?? null
    this._gmat = data.gmat ?? null
    this._sat = data.sat ?? null
    this._cat = data.cat ?? null
    this._gre = data.gre ?? null
    this._stat = data.stat ?? null
    this._ielts = data.ielts ?? null
    this._toefl = data.toefl ?? null
    this._pearsonTest = data.pearson_test ?? null
    this._camAdvTest = data.cam_adv_test ?? null
    this._interBac = data.inter_bac ?? null
  }

  get id() { return this._id }
  get userId() { return this._userId }
  get level() { return this._level }
  get major() { return this._major }
  get academicRate() { return this._academicRate }
  get gpa() { return this._gpa }
  get graduateYear() { return this._graduateYear }
  get act() { return this._act }
  get gmat() { return this._gmat }
  get sat() { return this._sat }
  get cat() { return this._cat }
  get gre() { return this._gre }
  get stat() { return this._stat }
  get ielts() { return this._ielts }
  get toefl() { return this._toefl }
  get pearsonTest() { return this._pearsonTest }
  get camAdvTest() { return this._camAdvTest }
  get interBac() { return this._interBac }

  // Business methods
  hasTestScores() {
    return [
      this._act, this._gmat, this._sat, this._cat, this._gre, this._stat,
      this._ielts, this._toefl, this._pearsonTest, this._camAdvTest, this._interBac,
    ].some(v => v !== null && v !== undefined)
  }

  getAcademicTestSummary() {
    const items = []
    if (this._act !== null) items.push(`ACT: ${this._act}`)
    if (this._gmat !== null) items.push(`GMAT: ${this._gmat}`)
    if (this._sat !== null) items.push(`SAT: ${this._sat}`)
    if (this._gre !== null) items.push(`GRE: ${this._gre}`)
    if (this._cat !== null) items.push(`CAT: ${this._cat}`)
    if (this._stat !== null) items.push(`STAT: ${this._stat}`)
    return items.join(' | ')
  }

  getLanguageTestSummary() {
    const items = []
    if (this._ielts !== null) items.push(`IELTS: ${this._ielts}`)
    if (this._toefl !== null) items.push(`TOEFL: ${this._toefl}`)
    if (this._pearsonTest !== null) items.push(`Pearson: ${this._pearsonTest}`)
    if (this._camAdvTest !== null) items.push(`Cambridge: ${this._camAdvTest}`)
    if (this._interBac !== null) items.push(`IB: ${this._interBac}`)
    return items.join(' | ')
  }

  getTestSummary() {
    return [this.getAcademicTestSummary(), this.getLanguageTestSummary()]
      .filter(Boolean)
      .join(' • ')
  }

  static fromAPI(data) {
    return new StudyBackground(data)
  }

  toPlainObject() {
    return {
      id: this._id,
      user_id: this._userId,
      level: this._level,
      major: this._major,
      academic_rate: this._academicRate,
      gpa: this._gpa,
      graduate_year: this._graduateYear,
      act: this._act,
      gmat: this._gmat,
      sat: this._sat,
      cat: this._cat,
      gre: this._gre,
      stat: this._stat,
      ielts: this._ielts,
      toefl: this._toefl,
      pearson_test: this._pearsonTest,
      cam_adv_test: this._camAdvTest,
      inter_bac: this._interBac,
    }
  }
}

export default StudyBackground
