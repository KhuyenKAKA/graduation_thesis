/**
 * Entity: Score
 * OOP wrapper around score data.
 */
export class Score {
  _id
  _indicatorId
  _scoreTypeId
  _rankInt
  _score
  _universityId
  _indicatorName
  _scoreTypeName

  constructor(data = {}) {
    this._id = data.id ?? null
    this._indicatorId = data.indicator_id ?? null
    this._scoreTypeId = data.score_type_id ?? null
    this._rankInt = data.rank_int ?? null
    this._score = data.score ?? null
    this._universityId = data.university_id ?? null
    this._indicatorName = data.indicator_name ?? null
    this._scoreTypeName = data.score_type_name ?? null
  }

  get id() { return this._id }
  get indicatorId() { return this._indicatorId }
  get scoreTypeId() { return this._scoreTypeId }
  get rankInt() { return this._rankInt }
  get score() { return this._score }
  get universityId() { return this._universityId }
  get indicatorName() { return this._indicatorName }
  get scoreTypeName() { return this._scoreTypeName }

  get formattedScore() {
    if (this._score === null || this._score === undefined) return 'N/A'
    return Number(this._score).toFixed(1)
  }

  get displayRank() {
    if (this._rankInt === null || this._rankInt === undefined) return 'N/A'
    return `#${this._rankInt}`
  }

  static fromAPI(data) {
    return new Score(data)
  }

  toPlainObject() {
    return {
      id: this._id,
      indicator_id: this._indicatorId,
      score_type_id: this._scoreTypeId,
      rank_int: this._rankInt,
      score: this._score,
      university_id: this._universityId,
      indicator_name: this._indicatorName,
      score_type_name: this._scoreTypeName,
    }
  }
}

export default Score
