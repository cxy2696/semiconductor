import Foundation
import SwiftUI

@MainActor
final class DashboardViewModel: ObservableObject {
    enum TextKey: String {
        case homeTitle
        case compareTitle
        case marketTitle
        case newsTitle
        case settingsTitle
        case decisionSupport
        case limitUpBoard
        case segmentDistribution
        case noLimitUp
        case globalSection
        case noGlobalItems
        case sourceOpen
        case onlyPicks
        case stocks
        case searchPrompt
        case localeTime
        case refreshNow
        case dataSection
        case profile
    }
    enum LocaleProfile: String, CaseIterable, Identifiable {
        case zhCN = "zh-CN|Asia/Shanghai"
        case enUS = "en-US|America/New_York"
        case deDE = "de-DE|Europe/Berlin"

        var id: String { rawValue }

        var title: String {
            switch self {
            case .zhCN: return "中文 + 中国时间"
            case .enUS: return "English + EST"
            case .deDE: return "Deutsch + CET"
            }
        }

        var localeIdentifier: String { rawValue.components(separatedBy: "|").first ?? "zh-CN" }
        var timeZoneIdentifier: String { rawValue.components(separatedBy: "|").last ?? "Asia/Shanghai" }
    }

    @Published private(set) var payload: DashboardPayload = .empty
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var query = ""
    @Published var onlyPicks = false
    @Published var selectedRegions: Set<String> = []
    @Published var selectedBusinessTypes: Set<String> = []
    @Published var localeProfile: LocaleProfile = .zhCN

    private let repository: DashboardRepository

    init(repository: DashboardRepository) {
        self.repository = repository
    }

    func text(_ key: TextKey) -> String {
        switch localeProfile {
        case .zhCN:
            switch key {
            case .homeTitle: return "看板"
            case .compareTitle: return "全球对比"
            case .marketTitle: return "市场"
            case .newsTitle: return "新闻"
            case .settingsTitle: return "设置"
            case .decisionSupport: return "决策辅助"
            case .limitUpBoard: return "涨停板观察"
            case .segmentDistribution: return "链段分布"
            case .noLimitUp: return "当前范围暂无涨停样本。"
            case .globalSection: return "全球对比"
            case .noGlobalItems: return "暂无全球对比信息。"
            case .sourceOpen: return "打开来源"
            case .onlyPicks: return "仅看入选"
            case .stocks: return "公司列表"
            case .searchPrompt: return "代码 / 公司 / 标签"
            case .localeTime: return "语言与时区"
            case .refreshNow: return "立即刷新"
            case .dataSection: return "数据"
            case .profile: return "配置"
            }
        case .enUS:
            switch key {
            case .homeTitle: return "Dashboard"
            case .compareTitle: return "Global Compare"
            case .marketTitle: return "Market"
            case .newsTitle: return "News"
            case .settingsTitle: return "Settings"
            case .decisionSupport: return "Decision Support"
            case .limitUpBoard: return "Limit-Up Board"
            case .segmentDistribution: return "Segment Distribution"
            case .noLimitUp: return "No limit-up stocks in current scope."
            case .globalSection: return "Global Comparison"
            case .noGlobalItems: return "No global comparison items available."
            case .sourceOpen: return "Open Source"
            case .onlyPicks: return "Only Picks"
            case .stocks: return "Stocks"
            case .searchPrompt: return "Code / Company / Tags"
            case .localeTime: return "Locale & Timezone"
            case .refreshNow: return "Refresh Now"
            case .dataSection: return "Data"
            case .profile: return "Profile"
            }
        case .deDE:
            switch key {
            case .homeTitle: return "Dashboard"
            case .compareTitle: return "Globaler Vergleich"
            case .marketTitle: return "Markt"
            case .newsTitle: return "Nachrichten"
            case .settingsTitle: return "Einstellungen"
            case .decisionSupport: return "Entscheidungshilfe"
            case .limitUpBoard: return "Limit-Up Beobachtung"
            case .segmentDistribution: return "Segmentverteilung"
            case .noLimitUp: return "Keine Limit-Up Titel im aktuellen Bereich."
            case .globalSection: return "Globaler Vergleich"
            case .noGlobalItems: return "Keine globalen Vergleichsdaten verfügbar."
            case .sourceOpen: return "Quelle öffnen"
            case .onlyPicks: return "Nur Auswahl"
            case .stocks: return "Aktien"
            case .searchPrompt: return "Code / Firma / Tags"
            case .localeTime: return "Sprache & Zeitzone"
            case .refreshNow: return "Jetzt aktualisieren"
            case .dataSection: return "Daten"
            case .profile: return "Profil"
            }
        }
    }

    func loadData(force: Bool) async {
        isLoading = true
        defer { isLoading = false }
        do {
            let fetched = try await repository.loadPayload(force: force)
            payload = fetched
            if selectedRegions.isEmpty {
                selectedRegions = Set(fetched.data.compactMap(\.region))
            }
            if selectedBusinessTypes.isEmpty {
                selectedBusinessTypes = Set(fetched.data.compactMap(\.businessType))
            }
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    var filteredStocks: [StockItem] {
        payload.data.filter { stock in
            let regionMatch = selectedRegions.isEmpty || selectedRegions.contains(stock.region ?? "")
            let bizMatch = selectedBusinessTypes.isEmpty || selectedBusinessTypes.contains(stock.businessType ?? "")
            let pickMatch = !onlyPicks || stock.isPick.value
            let q = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            let searchMatch: Bool
            if q.isEmpty {
                searchMatch = true
            } else {
                let haystack = [
                    stock.code, stock.name, stock.english ?? "", stock.businessType ?? "", stock.board ?? "", stock.investTags ?? ""
                ].joined(separator: " ").lowercased()
                searchMatch = haystack.contains(q)
            }
            return regionMatch && bizMatch && pickMatch && searchMatch
        }
    }

    var limitUpStocks: [StockItem] {
        filteredStocks.filter(\.isLimitUp).sorted { ($0.changePct ?? 0) > ($1.changePct ?? 0) }
    }

    var decisionCandidates: [StockItem] {
        filteredStocks.sorted { ($0.investScore ?? 0) > ($1.investScore ?? 0) }.prefix(8).map { $0 }
    }

    var regions: [String] {
        Set(payload.data.compactMap(\.region)).sorted()
    }

    var businessTypes: [String] {
        Set(payload.data.compactMap(\.businessType)).sorted()
    }
}
