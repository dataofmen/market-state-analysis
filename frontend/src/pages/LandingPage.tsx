import { Link } from 'react-router-dom'
import { TrendingUp, BarChart3, Shield, Zap } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <header className="container mx-auto px-4 py-16">
        <nav className="flex justify-between items-center mb-16">
          <h1 className="text-2xl font-bold text-primary-600">Market State Analysis</h1>
          <div className="space-x-4">
            <Link to="/login" className="text-gray-600 hover:text-primary-600">
              로그인
            </Link>
            <Link
              to="/register"
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
            >
              시작하기
            </Link>
          </div>
        </nav>

        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            시장 상태를 정확히 분석하여
            <br />
            <span className="text-primary-600">최적의 투자 전략</span>을 제시합니다
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            5가지 핵심 기술적 지표로 시장의 추세, 변동성, 위험도를 실시간 분석하고
            <br />
            현재 시장 상태에 맞는 맞춤형 투자 전략을 제공합니다
          </p>
          <Link
            to="/register"
            className="inline-block bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700"
          >
            무료로 시작하기
          </Link>
        </div>
      </header>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="추세 분석"
            description="ADX와 Bollinger Bands로 시장의 추세 강도와 방향을 정확히 파악"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="변동성 측정"
            description="ATR과 표준편차로 시장의 변동성을 실시간으로 모니터링"
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8" />}
            title="위험 관리"
            description="VIX 지표로 시장 위험도를 평가하고 포지션 크기를 자동 조절"
          />
          <FeatureCard
            icon={<Zap className="w-8 h-8" />}
            title="맞춤형 전략"
            description="12가지 시장 상태별 최적화된 투자 전략을 즉시 제공"
          />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">어떻게 작동하나요?</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              number="1"
              title="관심 종목 등록"
              description="분석하고 싶은 미국 주식 종목을 관심 목록에 추가하세요"
            />
            <StepCard
              number="2"
              title="실시간 분석"
              description="5가지 기술적 지표를 기반으로 시장 상태를 자동 분석합니다"
            />
            <StepCard
              number="3"
              title="전략 실행"
              description="현재 시장 상태에 맞는 최적의 투자 전략을 바로 적용하세요"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <h3 className="text-3xl font-bold mb-4">지금 바로 시작하세요</h3>
        <p className="text-xl text-gray-600 mb-8">
          체계적인 시장 분석으로 더 나은 투자 결정을 내리세요
        </p>
        <Link
          to="/register"
          className="inline-block bg-primary-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-700"
        >
          무료로 시작하기
        </Link>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Market State Analysis System. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="text-primary-600 mb-4">{icon}</div>
      <h4 className="text-lg font-semibold mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}

function StepCard({ number, title, description }: { number: string; title: string; description: string }) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-600 text-white text-xl font-bold mb-4">
        {number}
      </div>
      <h4 className="text-xl font-semibold mb-2">{title}</h4>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
