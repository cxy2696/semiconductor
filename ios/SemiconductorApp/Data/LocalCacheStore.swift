import Foundation

struct LocalCacheStore {
    private let fileName = "dashboard_cache.json"

    private var cacheURL: URL? {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask).first?.appendingPathComponent(fileName)
    }

    func save(_ payload: DashboardPayload) {
        guard let url = cacheURL else { return }
        do {
            let data = try JSONEncoder().encode(payload)
            try data.write(to: url, options: .atomic)
        } catch {
            // Cache failures are non-fatal for app flow.
        }
    }

    func load() -> DashboardPayload? {
        guard let url = cacheURL else { return nil }
        do {
            let data = try Data(contentsOf: url)
            return try JSONDecoder().decode(DashboardPayload.self, from: data)
        } catch {
            return nil
        }
    }
}
