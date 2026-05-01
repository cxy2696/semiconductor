import Foundation

actor DashboardRepository {
    private let networkClient: NetworkClient
    private let cacheStore: LocalCacheStore
    private(set) var lastRefresh: Date?

    static let defaultEndpoint = "https://cxy2696.github.io/semiconductor/latest_data.json"
    private let refreshInterval: TimeInterval = 60 * 60 * 12

    init(networkClient: NetworkClient, cacheStore: LocalCacheStore) {
        self.networkClient = networkClient
        self.cacheStore = cacheStore
    }

    func loadPayload(force: Bool, endpoint: String = DashboardRepository.defaultEndpoint) async throws -> DashboardPayload {
        if !force, let lastRefresh, Date().timeIntervalSince(lastRefresh) < refreshInterval, let cached = cacheStore.load() {
            return cached
        }

        do {
            let payload = try await networkClient.fetchPayload(from: endpoint)
            cacheStore.save(payload)
            lastRefresh = Date()
            return payload
        } catch {
            if let cached = cacheStore.load() {
                return cached
            }
            throw error
        }
    }
}
