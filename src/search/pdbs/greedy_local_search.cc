#include "greedy_local_search.h"

#include "utils.h"

#include "../plugins/plugin.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    GreedyLocalSearch::GreedyLocalSearch(const plugins::Options &opts) : PostHoc(opts),
                                                                         tie_breaking_operation(opts.get<GreedyTieBreakingOperation>("tie_breaking"))

    {
        utils::g_log << "Tie breaking: " << this->tie_breaking_operation << endl;
        this->number_of_relevant_and_valid_restrictions_by_operator.resize(this->operators.size());
        this->max_value_pdb_by_operator.resize(this->operators.size());
        this->pre_computed_times_to_increment_by_operator.resize(this->operators.size());
        this->pre_computed_performance_denominator_by_operator.resize(this->operators.size());
        for (const int &operator_id : this->operators)
        {
            if (this->operator_cost[operator_id] > 0)
            {
                this->non_zero_cost_operators.push_back(operator_id);
            }
        }
    }

    void GreedyLocalSearch::compute_post_hoc()
    {
        this->init_internal_attributes();
        this->update_operators_with_simple_restrictions();

        while (is_any_restriction_lower_bound_greater_than_zero())
        {
            int operator_id = get_best_operator();

            int times_to_increment = compute_times_to_increment(operator_id);
            operator_count[operator_id] += times_to_increment;

            update_lower_bounds_with_selected_operator(operator_id, times_to_increment);
        }
    }

    void GreedyLocalSearch::update_lower_bounds_with_selected_operator(int operator_id, int times_to_increment)
    {
        std::vector<int> restrictions_to_delete;
        for (int i = 0; i < this->number_of_relevant_and_valid_restrictions_by_operator[operator_id]; i++)
        {
            int restriction_id = this->relevant_restrictions_by_operator[operator_id][i];
            this->lower_bounds[restriction_id] -= times_to_increment * operator_cost[operator_id];
            this->lower_bounds_squared[restriction_id] = this->lower_bounds[restriction_id] * this->lower_bounds[restriction_id];
            if (this->lower_bounds[restriction_id] <= 0)
            {
                restrictions_to_delete.push_back(restriction_id);
            }
        }

        for (const int &restriction_id : restrictions_to_delete)
        {
            this->delete_restriction(restriction_id);
        }
    }

    float GreedyLocalSearch::compute_operator_performance(const int operator_id)
    {
        return this->number_of_relevant_and_valid_restrictions_by_operator[operator_id] / this->pre_computed_performance_denominator_by_operator[operator_id];
    }

    int GreedyLocalSearch::get_best_operator()
    {
        int best_operator_id = -1;
        float best_operator_performance = -1;
        int best_operator_tie_breaking = INT16_MIN;

        for (const int &operator_id : this->non_zero_cost_operators)
        {
            float operator_performance = this->compute_operator_performance(operator_id);

            if (best_operator_performance < operator_performance || best_operator_id == -1)
            {
                best_operator_id = operator_id;
                best_operator_performance = operator_performance;
                best_operator_tie_breaking = INT16_MIN;

                continue;
            }

            if (best_operator_performance == operator_performance)
            {
                if (best_operator_tie_breaking == INT16_MIN)
                {
                    best_operator_tie_breaking = this->compute_operator_tie_breaking(best_operator_id);
                }

                int operator_tie_breaking = this->compute_operator_tie_breaking(operator_id);
                if (best_operator_tie_breaking < operator_tie_breaking)
                {
                    best_operator_id = operator_id;
                    best_operator_tie_breaking = operator_tie_breaking;
                }
            }
        }

        return best_operator_id;
    }

    int GreedyLocalSearch::compute_times_to_increment(const int operator_id)
    {
        return this->pre_computed_times_to_increment_by_operator[operator_id];
    }

    void GreedyLocalSearch::update_operators_with_simple_restrictions()
    {
        std::vector<int> operators_to_update;
        for (const int &restriction_id : this->simple_restrictions_ids)
        {
            int operator_id = *this->relevant_operators_by_restriction[restriction_id].begin();

            // The code below does the same as the following commented code but in a faster way
            // int times_to_increment = (int)std::ceil((float)this->lower_bounds[restriction_id] / this->operator_cost[operator_id]);
            int times_to_increment = (this->lower_bounds[restriction_id] + this->operator_cost[operator_id] - 1) / this->operator_cost[operator_id];

            if (this->operator_count[operator_id] == 0)
            {
                operators_to_update.push_back(operator_id);
            }
            this->operator_count[operator_id] = std::max(this->operator_count[operator_id], times_to_increment);
        }

        for (const int &operator_id : operators_to_update)
        {
            this->update_lower_bounds_with_selected_operator(operator_id, this->operator_count[operator_id]);
        }
    }

    int GreedyLocalSearch::compute_operator_tie_breaking(const int operator_id)
    {
        switch (this->tie_breaking_operation)
        {
        case GreedyTieBreakingOperation::MAX_CONSTRAINT:
            return this->compute_tie_breaking_max_constraint(operator_id);
        case GreedyTieBreakingOperation::SUM_CONSTRAINTS:
            return this->compute_tie_breaking_sum_constraint(operator_id);
        case GreedyTieBreakingOperation::SUM_SQUARE_CONSTRAINTS:
            return this->compute_tie_breaking_sum_square_constraint(operator_id);
        }

        throw std::runtime_error("TieBreakingOperation not found");
    }

    int GreedyLocalSearch::compute_tie_breaking_max_constraint(const int operator_id)
    {
        int acc = 0;
        for (int i = 0; i < this->number_of_relevant_and_valid_restrictions_by_operator[operator_id]; i++)
        {
            int restriction_id = this->relevant_restrictions_by_operator[operator_id][i];
            acc = std::max(acc, this->lower_bounds[restriction_id]);
        }
        return acc;
    }

    int GreedyLocalSearch::compute_tie_breaking_sum_constraint(const int operator_id)
    {
        int acc = 0;
        for (int i = 0; i < this->number_of_relevant_and_valid_restrictions_by_operator[operator_id]; i++)
        {
            int restriction_id = this->relevant_restrictions_by_operator[operator_id][i];

            acc += this->lower_bounds[restriction_id];
        }
        return acc;
    }

    int GreedyLocalSearch::compute_tie_breaking_sum_square_constraint(const int operator_id)
    {
        int acc = 0;
        for (int i = 0; i < this->number_of_relevant_and_valid_restrictions_by_operator[operator_id]; i++)
        {
            int restriction_id = this->relevant_restrictions_by_operator[operator_id][i];
            acc += this->lower_bounds_squared[restriction_id];
        }
        return acc;
    }

    void GreedyLocalSearch::delete_restriction(int restriction_id)
    {
        this->restrictions_valid[restriction_id] = false;
        restrictions_with_lower_bound_greater_than_zero--;

        for (const int &operator_id : this->relevant_operators_by_restriction[restriction_id])
        {
            this->number_of_relevant_and_valid_restrictions_by_operator[operator_id]--;
            int i = this->restriction_position_on_relevant_restrictions_by_operator[operator_id][restriction_id];
            int j = this->number_of_relevant_and_valid_restrictions_by_operator[operator_id];
            if (i == j)
            {
                continue;
            }
            int other_restriction_id = this->relevant_restrictions_by_operator[operator_id][j];
            std::swap(this->relevant_restrictions_by_operator[operator_id][i], this->relevant_restrictions_by_operator[operator_id][j]);
            std::swap(this->restriction_position_on_relevant_restrictions_by_operator[operator_id][restriction_id], this->restriction_position_on_relevant_restrictions_by_operator[operator_id][other_restriction_id]);
        }
    }

    inline bool GreedyLocalSearch::is_restriction_deleted(int restriction_id)
    {
        return !this->restrictions_valid[restriction_id];
    }

    void GreedyLocalSearch::init_internal_attributes()
    {
        for (const int &operator_id : this->non_zero_cost_operators)
        {
            this->number_of_relevant_and_valid_restrictions_by_operator[operator_id] = this->relevant_restrictions_by_operator[operator_id].size();
            this->max_value_pdb_by_operator[operator_id] = 0;
            for (const int &restriction_id : this->relevant_restrictions_by_operator[operator_id])
            {
                if (this->max_value_pdb_by_operator[operator_id] < this->value_pdbs[restriction_id])
                {
                    this->max_value_pdb_by_operator[operator_id] = this->value_pdbs[restriction_id];
                }
            }
            this->pre_computed_times_to_increment_by_operator[operator_id] = (int)std::ceil((float)this->max_value_pdb_by_operator[operator_id] / this->operator_cost[operator_id]);
            this->pre_computed_performance_denominator_by_operator[operator_id] = this->operator_cost[operator_id] * this->pre_computed_times_to_increment_by_operator[operator_id];
        }

        this->restrictions_valid.assign(this->relevant_operators_by_restriction.size(), true);
        this->restrictions_with_lower_bound_greater_than_zero = this->relevant_operators_by_restriction.size();
        this->lower_bounds_squared.resize(this->restrictions_valid.size(), 0);
        for (size_t restriction_id = 0; restriction_id < this->relevant_operators_by_restriction.size(); restriction_id++)
        {
            this->lower_bounds_squared[restriction_id] = this->lower_bounds[restriction_id] * this->lower_bounds[restriction_id];
            if (this->lower_bounds[restriction_id] <= 0)
            {
                this->delete_restriction(restriction_id);
            }
        }
    }

    inline bool GreedyLocalSearch::is_any_restriction_lower_bound_greater_than_zero()
    {
        return this->restrictions_with_lower_bound_greater_than_zero > 0;
    }

    class GreedyLocalSearchFeature : public PostHocFeature<GreedyLocalSearch>
    {
    public:
        GreedyLocalSearchFeature() : PostHocFeature<GreedyLocalSearch>("glsh", "GreedyLocalSearch heuristic")
        {
            Feature::add_option<GreedyTieBreakingOperation>("tie_breaking",
                                                            "Operation to use for tie breaking when selecting best operator",
                                                            "sum_square_constraints");

            document_language_support("action costs", "supported");
            document_language_support("conditional effects", "not supported");
            document_language_support("axioms", "not supported");
            document_property("admissible", "no");
            document_property("consistent", "no");
            document_property("safe", "yes");
            document_property("preferred operators", "no");
        }
    };
    static plugins::FeaturePlugin<GreedyLocalSearchFeature> _plugin;
    static plugins::TypedEnumPlugin<GreedyTieBreakingOperation> _enum_tie_breaking_plugin({{"max_constraint", "max_constraint"}, {"sum_constraints", "sum_constraints"}, {"sum_square_constraints", "sum_square_constraints"}});
}
