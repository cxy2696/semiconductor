import SwiftUI

struct RootTabView: View {
    @EnvironmentObject private var viewModel: DashboardViewModel

    var body: some View {
        TabView {
            NavigationStack {
                HomeView()
            }
            .tabItem {
                Label(viewModel.text(.homeTitle), systemImage: "house")
            }

            NavigationStack {
                CompareView()
            }
            .tabItem {
                Label(viewModel.text(.compareTitle), systemImage: "globe")
            }

            NavigationStack {
                MarketView()
            }
            .tabItem {
                Label(viewModel.text(.marketTitle), systemImage: "list.bullet.rectangle")
            }

            NavigationStack {
                NewsView()
            }
            .tabItem {
                Label(viewModel.text(.newsTitle), systemImage: "newspaper")
            }

            NavigationStack {
                SettingsView()
            }
            .tabItem {
                Label(viewModel.text(.settingsTitle), systemImage: "gearshape")
            }
        }
        .tint(.blue)
    }
}
