"""多智能体分析 API 路由

提供基于17+智能体的股票分析接口
"""

from flask import Blueprint, jsonify, request
from src.agents.multi_agent import get_coordinator, analyze_stock

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/agent/analyze/<symbol>', methods=['GET'])
def analyze_with_agents(symbol):
    """使用多智能体分析股票

    Query params:
        use_mock: 是否使用模拟 (true/false, 默认 true)

    Args:
        symbol: 股票代码

    Returns:
        JSON 多智能体分析结果
    """
    try:
        use_mock = request.args.get('use_mock', 'true').lower() == 'true'

        coordinator = get_coordinator()
        result = coordinator.run_simple_analysis(symbol, use_mock=use_mock)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Analysis failed',
            'error': str(e)
        }), 500


@agent_bp.route('/agent/full-analysis/<symbol>', methods=['GET'])
def full_analysis_with_agents(symbol):
    """完整的多智能体分析 (使用LLM)

    Args:
        symbol: 股票代码

    Returns:
        JSON 完整分析结果
    """
    try:
        coordinator = get_coordinator()
        result = coordinator.run_stock_analysis(symbol)

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': result.to_dict()
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Full analysis failed',
            'error': str(e)
        }), 500


@agent_bp.route('/agent/team/<team_name>', methods=['GET'])
def run_single_agent(symbol, team_name):
    """运行单个智能体

    Args:
        symbol: 股票代码
        team_name: 智能体名称 (industry/risk/stock)

    Returns:
        JSON 智能体输出
    """
    try:
        coordinator = get_coordinator()

        # 根据团队名称运行不同的分析
        if team_name == 'industry':
            # 行业分析团队
            result = coordinator._run_industry_team(symbol, {})
        elif team_name == 'risk':
            # 风控团队
            result = coordinator._run_risk_assessment(symbol, {})
        elif team_name == 'stock':
            # 个股精选
            result = coordinator._run_stock_selection(symbol, {})
        else:
            return jsonify({
                'code': 400,
                'message': f'Unknown team: {team_name}'
            }), 400

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'team': team_name,
                'result': str(result)
            }
        })

    except Exception as e:
        return jsonify({
            'code': 500,
            'message': 'Agent execution failed',
            'error': str(e)
        }), 500


@agent_bp.route('/agent/teams', methods=['GET'])
def list_agents():
    """列出所有可用的智能体

    Returns:
        JSON 智能体列表
    """
    agents = {
        # 行业分析团队 (11个)
        'industry_team': [
            'macro_analyst',
            'fundamental_analyst',
            'technical_analyst',
            'insider_analyst',
            'research_analyst',
            'geo_analyst',
            'news_analyst',
            'bull_analyst',
            'bear_analyst',
            'contrarian_analyst',
            'industry_secretary'
        ],
        # 配置团队 (2个)
        'allocation_team': [
            'portfolio_trader',
            'allocation_secretary'
        ],
        # 风控团队 (3个)
        'risk_team': [
            'risk_scanner',
            'portfolio_risk_analyst',
            'risk_secretary'
        ],
        # 个股精选 (5个)
        'stock_selection_team': [
            'stock_screener',
            'financial_detective',
            'valuation_expert',
            'alpha_researcher',
            'stock_risk_analyst'
        ],
        # 交易执行 (1个)
        'execution_team': [
            'trade_executor'
        ],
        # 最终决策 (1个)
        'decision': [
            'final_decider'
        ]
    }

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': agents
    })


@agent_bp.route('/agent/team-details', methods=['GET'])
def get_team_details():
    """获取团队详细信息

    Returns:
        JSON 团队详细信息列表
    """
    teams = [
        {
            'id': 'industry_team',
            'name': '行业分析团队',
            'description': '负责宏观经济、行业趋势、技术面、消息面等全方位分析',
            'agent_count': 11,
            'color': '#3498db'
        },
        {
            'id': 'allocation_team',
            'name': '资产配置团队',
            'description': '负责根据行业判断进行仓位配置和调仓方案制定',
            'agent_count': 2,
            'color': '#9b59b6'
        },
        {
            'id': 'risk_team',
            'name': '风控团队',
            'description': '负责全市场风险扫描和组合风险评估',
            'agent_count': 3,
            'color': '#e74c3c'
        },
        {
            'id': 'stock_selection_team',
            'name': '个股精选团队',
            'description': '负责从行业中筛选优质个股，进行财务审核和估值',
            'agent_count': 5,
            'color': '#27ae60'
        },
        {
            'id': 'execution_team',
            'name': '交易执行团队',
            'description': '负责执行买卖指令，优化成交策略',
            'agent_count': 1,
            'color': '#f39c12'
        },
        {
            'id': 'decision',
            'name': '最终决策团队',
            'description': '综合所有分析结果，给出最终投资决策',
            'agent_count': 1,
            'color': '#1abc9c'
        }
    ]

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': teams
    })


# 智能体名称到提示词变量名的映射
AGENT_PROMPT_MAP = {
    'macro_analyst': ('PROMPT_MACRO_ANALYST', '宏观分析师', '分析利率走势、汇率变化、产业政策、宏观经济指标'),
    'fundamental_analyst': ('PROMPT_FUNDAMENTAL_ANALYST', '基本面分析师', '分析行业增长率、利润率、竞争格局、上下游关系'),
    'technical_analyst': ('PROMPT_TECHNICAL_ANALYST', '技术分析师', '分析支撑位压力位、趋势判断、技术指标、成交量'),
    'insider_analyst': ('PROMPT_INSIDER_ANALYST', '内部信息分析师', '追踪非公开信息、专家访谈、产业链动态'),
    'research_analyst': ('PROMPT_RESEARCH_ANALYST', '研报分析师', '汇总机构观点、目标价、评级分布'),
    'geo_analyst': ('PROMPT_GEOPOLITICAL_ANALYST', '地缘政治分析师', '分析国际贸易关系、制裁政策、汇率波动'),
    'news_analyst': ('PROMPT_MARKET_NEWS_ANALYST', '市场信息分析师', '新闻情感分析、舆论热度、突发消息'),
    'bull_analyst': ('PROMPT_BULL_ANALYST', '多头研究员', '寻找买入理由、分析上涨逻辑'),
    'bear_analyst': ('PROMPT_BEAR_ANALYST', '空头研究员', '寻找风险理由、分析下跌风险'),
    'contrarian_analyst': ('PROMPT_CONTRARIAN_ANALYST', '核心矛盾研究员', '提炼核心矛盾、判断主要矛盾变化'),
    'industry_secretary': ('PROMPT_INDUSTRY_SECRETARY', '行业秘书', '汇总分析师观点、生成行业判断报告'),
    'portfolio_trader': ('PROMPT_PORTFOLIO_TRADER', '配置交易员', '仓位配置、调仓方案制定'),
    'allocation_secretary': ('PROMPT_ALLOCATION_SECRETARY', '配置秘书', '将调仓指令转化为易读建议书'),
    'risk_scanner': ('PROMPT_RISK_SCANNER', '风险扫描员', '全市场风险扫描、风险事件监控'),
    'portfolio_risk_analyst': ('PROMPT_PORTFOLIO_RISK_ANALYST', '组合风险分析师', '分析集中度风险、相关性风险、流动性风险'),
    'risk_secretary': ('PROMPT_RISK_SECRETARY', '风控秘书', '给出最终风险评级、交易许可'),
    'stock_screener': ('PROMPT_STOCK_SCREENER', '个股筛选器', '量化选股、筛选条件设置'),
    'financial_detective': ('PROMPT_FINANCIAL_DETECTIVE', '财务侦探', '审核财务数据、营收真实性、负债率'),
    'valuation_expert': ('PROMPT_VALUATION_EXPERT', '估值专家', 'DCF估值、PE估值、PS估值'),
    'alpha_researcher': ('PROMPT_ALPHA_RESEARCHER', 'Alpha研究员', '寻找超额收益来源、竞争优势、护城河'),
    'stock_risk_analyst': ('PROMPT_STOCK_RISK_ANALYST', '个股风控师', '检查违规记录、减持风险、ESG风险'),
    'trade_executor': ('PROMPT_TRADER', '交易执行员', '执行买卖指令、成交策略'),
    'final_decider': ('PROMPT_FINAL_DECISION', '最终决策者', '综合所有分析给出投资决策')
}


@agent_bp.route('/agent/prompt/<agent_name>', methods=['GET'])
def get_agent_prompt(agent_name):
    """获取智能体提示词

    Args:
        agent_name: 智能体名称

    Returns:
        JSON 智能体提示词信息
    """
    if agent_name not in AGENT_PROMPT_MAP:
        return jsonify({
            'code': 404,
            'message': f'Agent not found: {agent_name}'
        }), 404

    prompt_var, agent_title, agent_desc = AGENT_PROMPT_MAP[agent_name]

    # 动态获取提示词
    from config import prompts
    prompt_text = getattr(prompts, prompt_var, '')

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'agent_name': agent_name,
            'agent_title': agent_title,
            'description': agent_desc,
            'prompt': prompt_text,
            'prompt_variable': prompt_var
        }
    })


@agent_bp.route('/agent/prompt/<agent_name>', methods=['POST'])
def update_agent_prompt(agent_name):
    """更新智能体提示词

    Args:
        agent_name: 智能体名称

    Request body:
        prompt: 新的提示词内容

    Returns:
        JSON 更新结果
    """
    if agent_name not in AGENT_PROMPT_MAP:
        return jsonify({
            'code': 404,
            'message': f'Agent not found: {agent_name}'
        }), 404

    data = request.get_json()
    new_prompt = data.get('prompt', '')

    if not new_prompt:
        return jsonify({
            'code': 400,
            'message': 'Prompt content is required'
        }), 400

    # 更新提示词
    prompt_var = AGENT_PROMPT_MAP[agent_name][0]
    setattr(prompts, prompt_var, new_prompt)

    # 保存到文件
    try:
        prompts.save_prompts()
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'Failed to save prompts: {str(e)}'
        }), 500

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {'agent_name': agent_name, 'prompt': new_prompt}
    })
