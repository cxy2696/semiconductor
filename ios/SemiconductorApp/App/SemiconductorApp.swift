import SwiftUI

@main
struct SemiconductorApp: App {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var viewModel = DashboardViewModel(
        repository: DashboardRepository(
            networkClient: NetworkClient(),
            cacheStore: LocalCacheStore()
        )
    )

    var body: some Scene {
        WindowGroup {
            RootTabView()
                .environmentObject(viewModel)
                .task {
                    await viewModel.loadData(force: false)
                }
        }
        .onChange(of: scenePhase) { _, newPhase in
            guard newPhase == .active else { return }
            Task {
                await viewModel.loadData(force: false)
            }
        }
    }
}
