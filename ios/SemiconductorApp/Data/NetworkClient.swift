import Foundation

struct NetworkClient {
    enum NetworkError: LocalizedError {
        case invalidURL
        case badStatus(Int)
        case decodingFailed

        var errorDescription: String? {
            switch self {
            case .invalidURL:
                return "Invalid data URL."
            case .badStatus(let code):
                return "Remote responded with status \(code)."
            case .decodingFailed:
                return "Failed to decode dashboard payload."
            }
        }
    }

    func fetchPayload(from endpoint: String) async throws -> DashboardPayload {
        guard var components = URLComponents(string: endpoint) else {
            throw NetworkError.invalidURL
        }
        components.queryItems = [URLQueryItem(name: "_ts", value: String(Int(Date().timeIntervalSince1970)))]
        guard let url = components.url else { throw NetworkError.invalidURL }

        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse else {
            throw NetworkError.badStatus(-1)
        }
        guard (200..<300).contains(http.statusCode) else {
            throw NetworkError.badStatus(http.statusCode)
        }

        let decoder = JSONDecoder()
        do {
            return try decoder.decode(DashboardPayload.self, from: data)
        } catch {
            throw NetworkError.decodingFailed
        }
    }
}
