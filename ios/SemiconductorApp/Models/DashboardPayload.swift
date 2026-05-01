import Foundation

struct DashboardPayload: Codable {
    let data: [StockItem]
    let newsPool: [NewsItem]
    let klineData: [String: KLineSeries]
    let industryIntro: [String]
    let industryBasics: [IndustryTerm]
    let industrySourceRefs: [SourceRef]
    let industryIntroSource: String
    let globalCompareItems: [GlobalCompareItem]
    let globalCompareRefs: [SourceRef]
    let dataTime: String
    let dataTimeISO: String

    enum CodingKeys: String, CodingKey {
        case data
        case newsPool = "news_pool"
        case klineData = "kline_data"
        case industryIntro = "industry_intro"
        case industryBasics = "industry_basics"
        case industrySourceRefs = "industry_source_refs"
        case industryIntroSource = "industry_intro_source"
        case globalCompareItems = "global_compare_items"
        case globalCompareRefs = "global_compare_refs"
        case dataTime = "data_time"
        case dataTimeISO = "data_time_iso"
    }
}

struct StockItem: Codable, Identifiable, Hashable {
    let code: String
    let name: String
    let english: String?
    let region: String?
    let businessType: String?
    let website: String?
    let price: Double?
    let peTrailing: Double?
    let peForward: Double?
    let volume: Double?
    let marketCap: Double?
    let high52: Double?
    let low52: Double?
    let changePct: Double?
    let board: String?
    let chainSegment: String?
    let investScore: Int?
    let investGrade: String?
    let investTags: String?
    let investReason: String?
    let isPick: BoolLike

    var id: String { code }

    var scoreTier: ScoreTier {
        let score = investScore ?? 0
        if score >= 80 { return .high }
        if score >= 65 { return .medium }
        return .low
    }

    var isLimitUp: Bool {
        (changePct ?? 0) >= 9.5
    }

    enum CodingKeys: String, CodingKey {
        case code, name, english, region, website, board
        case businessType = "business_type"
        case price
        case peTrailing = "pe_trailing"
        case peForward = "pe_forward"
        case volume
        case marketCap = "market_cap"
        case high52
        case low52
        case changePct = "change_pct"
        case chainSegment = "chain_segment"
        case investScore = "invest_score"
        case investGrade = "invest_grade"
        case investTags = "invest_tags"
        case investReason = "invest_reason"
        case isPick = "is_pick"
    }
}

enum ScoreTier: Equatable {
    case high
    case medium
    case low
}

enum BoolLike: Codable, Hashable {
    case bool(Bool)
    case int(Int)
    case string(String)
    case none

    var value: Bool {
        switch self {
        case .bool(let v):
            return v
        case .int(let v):
            return v == 1
        case .string(let v):
            return v.lowercased() == "true" || v == "1"
        case .none:
            return false
        }
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let v = try? container.decode(Bool.self) {
            self = .bool(v)
        } else if let v = try? container.decode(Int.self) {
            self = .int(v)
        } else if let v = try? container.decode(String.self) {
            self = .string(v)
        } else {
            self = .none
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .bool(let v):
            try container.encode(v)
        case .int(let v):
            try container.encode(v)
        case .string(let v):
            try container.encode(v)
        case .none:
            try container.encodeNil()
        }
    }
}

struct NewsItem: Codable, Identifiable, Hashable {
    let title: String
    let link: String
    let date: String
    var id: String { "\(title)|\(link)" }
}

struct KLineSeries: Codable, Hashable {
    let code: String?
    let marketCap: Double?
    let businessType: String?
    let chainSegment: String?
    let date: [String]?
    let open: [Double]?
    let high: [Double]?
    let low: [Double]?
    let close: [Double]?
    let change30d: Double?

    enum CodingKeys: String, CodingKey {
        case code
        case marketCap = "market_cap"
        case businessType = "business_type"
        case chainSegment = "chain_segment"
        case date, open, high, low, close
        case change30d = "change_30d"
    }
}

struct IndustryTerm: Codable, Identifiable, Hashable {
    let term: String
    let desc: String
    var id: String { term + desc.prefix(12) }
}

struct SourceRef: Codable, Identifiable, Hashable {
    let name: String
    let url: String
    var id: String { "\(name)|\(url)" }
}

struct GlobalCompareItem: Codable, Identifiable, Hashable {
    let sourceName: String?
    let title: String
    let summary: String?
    let url: String
    var id: String { "\(title)|\(url)" }

    enum CodingKeys: String, CodingKey {
        case sourceName = "source_name"
        case title, summary, url
    }
}

extension DashboardPayload {
    static var empty: DashboardPayload {
        DashboardPayload(
            data: [],
            newsPool: [],
            klineData: [:],
            industryIntro: [],
            industryBasics: [],
            industrySourceRefs: [],
            industryIntroSource: "",
            globalCompareItems: [],
            globalCompareRefs: [],
            dataTime: "",
            dataTimeISO: ""
        )
    }
}
