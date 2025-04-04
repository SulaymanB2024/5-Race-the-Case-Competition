import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set, Union
import pandas as pd

#pip install numpy
#pip install matplotlib
#pip install dataclasses
#pip install pandas



@dataclass
class Project:
    name: str
    description: str
    potential_value: List[str]
    level_of_effort: str
    timeline_months: float
    cost_category: str
    cost_estimate: float  # Estimated cost in dollars
    
    # Additional attributes for analysis
    dependencies: List[str] = None
    strategic_priority: int = 0  # 1-10 scale
    risk_level: int = 0  # 1-10 scale
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class DecisionFramework:
    def __init__(self):
        self.projects = {}
        self.viability_thresholds = {
            'max_timeline': 24,  # months
            'max_cost': 2000000,  # dollars
            'max_effort': 'High',
            'effort_levels': {'Low': 1, 'Medium': 2, 'High': 3}
        }
    
    def add_project(self, project: Project):
        """Add a project to the framework"""
        self.projects[project.name] = project
    
    def filter_nonviable_projects(self) -> Dict[str, Project]:
        """Filter out non-viable projects based on constraints"""
        viable_projects = {}
        nonviable_projects = {}
        
        for name, project in self.projects.items():
            # Check if project exceeds any threshold
            if (project.timeline_months > self.viability_thresholds['max_timeline'] or
                project.cost_estimate > self.viability_thresholds['max_cost'] or
                self.viability_thresholds['effort_levels'].get(project.level_of_effort, 0) > 
                self.viability_thresholds['effort_levels'].get(self.viability_thresholds['max_effort'], 0)):
                nonviable_projects[name] = project
            else:
                viable_projects[name] = project
        
        print(f"Filtered {len(nonviable_projects)} non-viable projects out of {len(self.projects)} total projects")
        return viable_projects
    
    def analyze_nonviability(self, nonviable_projects: Dict[str, Project]) -> Dict[str, List[str]]:
        """Analyze why projects are non-viable"""
        nonviability_reasons = {}
        
        for name, project in nonviable_projects.items():
            reasons = []
            
            if project.timeline_months > self.viability_thresholds['max_timeline']:
                reasons.append(f"Timeline ({project.timeline_months} months) exceeds maximum ({self.viability_thresholds['max_timeline']} months)")
            
            if project.cost_estimate > self.viability_thresholds['max_cost']:
                reasons.append(f"Cost (${project.cost_estimate:,.2f}) exceeds maximum (${self.viability_thresholds['max_cost']:,.2f})")
            
            if (self.viability_thresholds['effort_levels'].get(project.level_of_effort, 0) > 
                self.viability_thresholds['effort_levels'].get(self.viability_thresholds['max_effort'], 0)):
                reasons.append(f"Effort level ({project.level_of_effort}) exceeds maximum ({self.viability_thresholds['max_effort']})")
            
            nonviability_reasons[name] = reasons
        
        return nonviability_reasons
    
    def calculate_roi_score(self, project: Project) -> float:
        """Calculate a simplified ROI score based on potential value vs cost and effort"""
        # This is a simplified model - in real applications, you'd have more sophisticated ROI calculations
        value_score = len(project.potential_value) * 10  # Each value point is worth 10 points
        effort_penalty = self.viability_thresholds['effort_levels'].get(project.level_of_effort, 0) * 5
        time_penalty = project.timeline_months * 0.5
        cost_penalty = project.cost_estimate / 100000  # Each $100k costs 1 point
        
        roi_score = value_score - effort_penalty - time_penalty - cost_penalty
        return roi_score
    
    def build_payoff_matrix(self, projects: Dict[str, Project], capital_constraint: float) -> Tuple[np.ndarray, List[str]]:
        """
        Build a payoff matrix for game theory analysis
        
        The matrix represents the strategic interactions between different project combinations
        under capital constraints.
        """
        # Get viable project combinations under capital constraint
        viable_combinations = []
        project_names = list(projects.keys())
        
        # Generate all possible project combinations
        from itertools import combinations
        for r in range(1, len(project_names) + 1):
            for combo in combinations(project_names, r):
                total_cost = sum(projects[p].cost_estimate for p in combo)
                if total_cost <= capital_constraint:
                    viable_combinations.append(combo)
        
        # Create payoff matrix
        n = len(viable_combinations)
        payoff_matrix = np.zeros((n, n))
        
        # Calculate payoffs for each combination against others
        for i, combo1 in enumerate(viable_combinations):
            for j, combo2 in enumerate(viable_combinations):
                # Self-comparison - calculate ROI score
                if i == j:
                    payoff_matrix[i, j] = sum(self.calculate_roi_score(projects[p]) for p in combo1)
                # Different combinations - calculate strategic advantage
                else:
                    # Projects in combo1 but not in combo2 (unique advantage)
                    unique_to_1 = set(combo1) - set(combo2)
                    # Projects in both combinations (shared value)
                    common = set(combo1) & set(combo2)
                    # Calculate advantage score
                    advantage_score = sum(self.calculate_roi_score(projects[p]) * 1.2 for p in unique_to_1)
                    common_score = sum(self.calculate_roi_score(projects[p]) * 0.8 for p in common)
                    payoff_matrix[i, j] = advantage_score + common_score
        
        return payoff_matrix, viable_combinations
    
    def find_nash_equilibrium(self, payoff_matrix: np.ndarray) -> List[int]:
        """Find Nash equilibrium in the payoff matrix"""
        n = payoff_matrix.shape[0]
        equilibria = []
        
        for i in range(n):
            # Check if strategy i is a best response for player 1
            if np.all(payoff_matrix[i, :] >= np.max(payoff_matrix[:, :], axis=0) - 0.001):
                # Check if strategy i is also a best response for player 2
                if np.all(payoff_matrix[:, i] <= np.max(payoff_matrix[:, :], axis=1) + 0.001):
                    equilibria.append(i)
        
        return equilibria
    
    def analyze_interdependencies(self, projects: Dict[str, Project]) -> Dict[str, Set[str]]:
        """Analyze project interdependencies"""
        dependency_graph = {}
        
        for name, project in projects.items():
            dependency_graph[name] = set(project.dependencies)
        
        # Find indirect dependencies through transitive closure
        for k in dependency_graph:
            for i in dependency_graph:
                if k in dependency_graph[i]:
                    dependency_graph[i].update(dependency_graph[k])
        
        return dependency_graph
    
    def simulate_branching_paths(self, 
                                projects: Dict[str, Project], 
                                initial_capital: float, 
                                time_horizon: int = 36) -> Dict[str, Dict]:
        """
        Simulate different branching paths for project selection over time
        
        Args:
            projects: Dictionary of projects
            initial_capital: Starting capital
            time_horizon: Time horizon in months
            
        Returns:
            Dictionary of different paths and their outcomes
        """
        # Sort projects by ROI score
        project_roi = {name: self.calculate_roi_score(project) for name, project in projects.items()}
        sorted_projects = sorted(project_roi.items(), key=lambda x: x[1], reverse=True)
        
        # Define different strategies
        strategies = {
            "high_roi_first": [p[0] for p in sorted_projects],
            "low_cost_first": sorted([p for p in projects.items()], key=lambda x: x[1].cost_estimate),
            "quick_wins": sorted([p for p in projects.items()], key=lambda x: x[1].timeline_months)
        }
        
        results = {}
        
        # Simulate each strategy
        for strategy_name, project_order in strategies.items():
            capital_remaining = initial_capital
            months_used = 0
            projects_selected = []
            total_roi = 0
            
            for project_name in project_order:
                project = projects[project_name]
                
                # Check if we can afford this project (money and time)
                if (project.cost_estimate <= capital_remaining and 
                    months_used + project.timeline_months <= time_horizon):
                    # Add project to our selection
                    projects_selected.append(project_name)
                    capital_remaining -= project.cost_estimate
                    months_used += project.timeline_months
                    total_roi += project_roi[project_name]
            
            results[strategy_name] = {
                "projects": projects_selected,
                "capital_used": initial_capital - capital_remaining,
                "capital_remaining": capital_remaining,
                "months_used": months_used,
                "total_roi": total_roi
            }
        
        return results

    def visualize_project_comparison(self, projects: Dict[str, Project]):
        """Visualize project comparison based on cost, timeline, and ROI"""
        names = list(projects.keys())
        costs = [p.cost_estimate / 1000 for p in projects.values()]  # Convert to thousands
        timelines = [p.timeline_months for p in projects.values()]
        roi_scores = [self.calculate_roi_score(p) for p in projects.values()]
        
        # Normalize ROI scores for bubble size (all positive)
        min_roi = min(roi_scores)
        normalized_roi = [r - min_roi + 10 for r in roi_scores]  # Add 10 to ensure positive values
        
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(costs, timelines, s=normalized_roi*20, alpha=0.6)
        
        # Add project labels
        for i, name in enumerate(names):
            plt.annotate(name, (costs[i], timelines[i]), 
                        fontsize=8, ha='center', va='center')
        
        plt.xlabel('Cost (thousands $)')
        plt.ylabel('Timeline (months)')
        plt.title('Project Comparison: Cost vs Timeline vs ROI')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add colorbar legend
        plt.colorbar(scatter, label='ROI Score')
        
        plt.tight_layout()
        plt.show()

# Example usage with Beauty First Cosmetics data
def create_bfc_projects():
    """Create projects based on the Beauty First Cosmetics example"""
    projects = [
        Project(
            name="New ERP Implementation",
            description="Integrate inventory management and order fulfillment operations for consumers",
            potential_value=[
                "Integrate inventory management and order fulfillment operations for consumers",
                "Obtain full visibility into key business processes through access to real-time, centralized data",
                "Enhance decision-making and planning through access to consolidated metrics and reports"
            ],
            level_of_effort="High",
            timeline_months=17.5,  # 15-20 months average
            cost_category="$$$$",
            cost_estimate=1500000,  # Estimated for $$$$ category
            dependencies=[],
            strategic_priority=9,
            risk_level=8
        ),
        Project(
            name="IT Infrastructure Upgrade",
            description="Upgrade servers, network equipment, storage",
            potential_value=[
                "Increase capacity to support new applications and services",
                "Improve efficiency with next-generation hardware and monitoring tools",
                "Offset investment costs with lower energy consumption and smaller data center footprint"
            ],
            level_of_effort="High",
            timeline_months=15,  # 12-18 months average
            cost_category="$$$",
            cost_estimate=750000,  # Estimated for $$$ category
            dependencies=[],
            strategic_priority=7,
            risk_level=6
        ),
        Project(
            name="Agile and DevOps Transformation",
            description="Transform development processes to Agile and DevOps methodologies",
            potential_value=[
                "Greater agility and speed; reduced time to market",
                "Allow application sponsors, developers, and users to maintain a faster and consistent pace of development and release",
                "Deeper interaction with customer base"
            ],
            level_of_effort="High",
            timeline_months=12,
            cost_category="$$$$",
            cost_estimate=1200000,  # Estimated for $$$$ category
            dependencies=[],
            strategic_priority=8,
            risk_level=7
        ),
        Project(
            name="Customer Experience Transformation",
            description="Expand customer service centers and enhance relationships",
            potential_value=[
                "Expand customer service centers and hire diligent representatives focusing on enhancing relationships",
                "Invest in new tools/technologies to increase focus on customer experience",
                "Expand brand/customer loyalty and increase revenue"
            ],
            level_of_effort="High",
            timeline_months=15,  # 12-18 months average
            cost_category="$$$",
            cost_estimate=800000,  # Estimated for $$$ category
            dependencies=[],
            strategic_priority=9,
            risk_level=5
        ),
        Project(
            name="Cybersecurity Strategy & Assessment",
            description="Provide clarity around security strategy and policy",
            potential_value=[
                "Protect and secure data and mitigate the risk of customer data and proprietary information from being compromised",
                "Identify potential vulnerabilities/weaknesses on Internet-accessible systems"
            ],
            level_of_effort="Medium",
            timeline_months=3.5,  # 3-4 months average
            cost_category="$$",
            cost_estimate=350000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=8,
            risk_level=9
        ),
        Project(
            name="AP Recovery Review",
            description="Identify and recover financial leakage",
            potential_value=[
                "Identify and recover financial leakage in the form of duplicate payments, unused credit memos, and lost or missed discounts",
                "Determine opportunities for working capital improvement",
                "Identify procurement and accounts payable process improvements"
            ],
            level_of_effort="Medium",
            timeline_months=3.5,  # 3-4 months average
            cost_category="$$",
            cost_estimate=300000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=6,
            risk_level=4
        ),
        Project(
            name="International Risk & Compliance Function",
            description="Enhance regulatory standing, manage risks, and comply with laws",
            potential_value=[
                "Enhance regulatory standing, manage risks, and comply with laws, regulations, and policies",
                "Avoid penalties of non-compliance and potential business disruptions and protect reputation"
            ],
            level_of_effort="Medium",
            timeline_months=4,
            cost_category="$$",
            cost_estimate=350000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=7,
            risk_level=8
        ),
        Project(
            name="Data Privacy and Resiliency",
            description="Maintain compliance with applicable privacy laws and regulations",
            potential_value=[
                "Avoid fines by maintaining compliance with applicable privacy laws and regulations",
                "Limit the impact and disruption to operations in the event of a data breach",
                "Increase consumer data reliability"
            ],
            level_of_effort="Medium",
            timeline_months=5,  # 4-6 months average
            cost_category="$$",
            cost_estimate=400000,  # Estimated for $$ category
            dependencies=["Cybersecurity Strategy & Assessment"],
            strategic_priority=8,
            risk_level=9
        ),
        Project(
            name="Customize Existing ERP System",
            description="Leverage existing ERP infrastructure to meet BFC's evolving business requirements",
            potential_value=[
                "Leverage existing ERP infrastructure to meet BFC's evolving business requirements",
                "Modify internal functionality to accommodate BFC's global expansion",
                "Update scalability factor to ensure the deliverance of reliable data with low latency"
            ],
            level_of_effort="Medium",
            timeline_months=9,  # 8-10 months average
            cost_category="$$",
            cost_estimate=400000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=7,
            risk_level=6
        ),
        Project(
            name="Non-Electronic Processing with RPA Implementation",
            description="Automate inventory analysis from requisition to distribution",
            potential_value=[
                "Automate inventory analysis from requisition to distribution to inventory velocity",
                "Provide management with enhanced reporting capabilities",
                "Increase accuracy in procurement, improve efficiency in recording"
            ],
            level_of_effort="Medium",
            timeline_months=5,  # 4-6 months average
            cost_category="$$",
            cost_estimate=350000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=6,
            risk_level=5
        ),
        Project(
            name="Procurement Transformation",
            description="Perform spend analysis to effectively manage direct and indirect costs",
            potential_value=[
                "Perform spend analysis to effectively manage direct and indirect costs, increasing ROI",
                "Enhance third-party vendor management assessment"
            ],
            level_of_effort="Medium",
            timeline_months=7,  # 6-8 months average
            cost_category="$$$",
            cost_estimate=600000,  # Estimated for $$$ category
            dependencies=["AP Recovery Review"],
            strategic_priority=7,
            risk_level=6
        ),
        Project(
            name="Logistics and Fulfillment Transformation",
            description="Optimize transportation type/medium and routes",
            potential_value=[
                "Optimize transportation type/medium and routes, resulting in faster and more cost-efficient shipping",
                "Provide evaluation of potential strategic sites"
            ],
            level_of_effort="Medium",
            timeline_months=7,  # 6-8 months average
            cost_category="$$$",
            cost_estimate=650000,  # Estimated for $$$ category
            dependencies=[],
            strategic_priority=8,
            risk_level=7
        ),
        Project(
            name="Selectively Onboard Managed Services Partners",
            description="Scalable resources to meet changing and seasonal demands",
            potential_value=[
                "Scalable resources to meet changing and seasonal demands",
                "Flexible cost structure to manage expenses and investment",
                "Focus on core capabilities and acquire expertise"
            ],
            level_of_effort="Medium",
            timeline_months=7,  # 6-8 months average
            cost_category="$$",
            cost_estimate=450000,  # Estimated for $$ category
            dependencies=[],
            strategic_priority=6,
            risk_level=5
        )
    ]
    
    return {project.name: project for project in projects}

def main():
    # Create the decision framework
    framework = DecisionFramework()
    
    # Add BFC projects
    bfc_projects = create_bfc_projects()
    for project in bfc_projects.values():
        framework.add_project(project)
    
    print(f"Loaded {len(bfc_projects)} projects from Beauty First Cosmetics")
    
    # Filter non-viable projects
    viable_projects = framework.filter_nonviable_projects()
    
    # Analyze why projects are non-viable
    nonviable_projects = {name: project for name, project in framework.projects.items() 
                         if name not in viable_projects}
    nonviability_reasons = framework.analyze_nonviability(nonviable_projects)
    
    print("\nNon-viable projects and reasons:")
    for project, reasons in nonviability_reasons.items():
        print(f"- {project}:")
        for reason in reasons:
            print(f"  * {reason}")
    
    # Calculate ROI scores for viable projects
    print("\nROI scores for viable projects:")
    for name, project in viable_projects.items():
        roi = framework.calculate_roi_score(project)
        print(f"- {name}: {roi:.2f}")
    
    # Build payoff matrix for game theory analysis
    capital_constraint = 2000000  # $2 million
    payoff_matrix, viable_combinations = framework.build_payoff_matrix(viable_projects, capital_constraint)
    
    print("\nGame Theory Analysis:")
    print(f"Found {len(viable_combinations)} viable project combinations under ${capital_constraint:,} capital constraint")
    
    # Find Nash equilibrium
    equilibria = framework.find_nash_equilibrium(payoff_matrix)
    print(f"Found {len(equilibria)} Nash equilibria")
    
    if equilibria:
        print("\nOptimal project combinations (Nash equilibria):")
        for eq in equilibria:
            combo = viable_combinations[eq]
            total_cost = sum(viable_projects[p].cost_estimate for p in combo)
            print(f"- Combination: {', '.join(combo)}")
            print(f"  Total cost: ${total_cost:,.2f}")
            print(f"  Payoff score: {payoff_matrix[eq, eq]:.2f}")
    
    # Analyze interdependencies
    dependency_graph = framework.analyze_interdependencies(viable_projects)
    
    print("\nProject Dependencies:")
    for project, dependencies in dependency_graph.items():
        if dependencies:
            print(f"- {project} depends on: {', '.join(dependencies)}")
    
    # Simulate branching paths
    print("\nSimulating different project selection strategies:")
    branching_results = framework.simulate_branching_paths(
        viable_projects, 
        initial_capital=3000000,  # $3 million
        time_horizon=24  # 24 months
    )
    
    for strategy, results in branching_results.items():
        print(f"\nStrategy: {strategy}")
        print(f"- Projects selected: {', '.join(results['projects'])}")
        print(f"- Capital used: ${results['capital_used']:,.2f}")
        print(f"- Capital remaining: ${results['capital_remaining']:,.2f}")
        print(f"- Months used: {results['months_used']}")
        print(f"- Total ROI score: {results['total_roi']:.2f}")
    
    # Visualize project comparison
    framework.visualize_project_comparison(viable_projects)
    
    # Create a DataFrame for easier analysis
    project_data = []
    for name, project in viable_projects.items():
        project_data.append({
            'Name': name,
            'Cost': project.cost_estimate,
            'Timeline': project.timeline_months,
            'Effort': project.level_of_effort,
            'ROI Score': framework.calculate_roi_score(project),
            'Dependencies': len(project.dependencies),
            'Strategic Priority': project.strategic_priority,
            'Risk Level': project.risk_level
        })
    
    df = pd.DataFrame(project_data)
    print("\nProject Data Summary:")
    print(df.sort_values('ROI Score', ascending=False))

if __name__ == "__main__":
    main()
