#include "post_hoc.h"

#include "pattern_generator.h"
#include "utils.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    PostHoc::PostHoc(const plugins::Options &opts) : Heuristic(opts),
                                                     seed(opts.get<int>("seed")),
                                                     verbose(opts.get<bool>("verbose"))
    {
        std::srand(seed);
        shared_ptr<PatternCollectionGenerator> pattern_generator =
            opts.get<shared_ptr<PatternCollectionGenerator>>("patterns");
        PatternCollectionInformation pci = pattern_generator->generate(task);

        pdbs = pci.get_pdbs();
        state = nullptr;

        get_restrictions();

        if (verbose)
        {
            this->print_info();
        }
    }

    void PostHoc::get_restrictions()
    {
        TaskProxy task_proxy = TaskProxy(*task);

        // operators and costs
        for (OperatorProxy op : task_proxy.get_operators())
        {
            operators.push_back(op.get_id());
            operator_cost.push_back(op.get_cost());
        }

        // restrictions from pdbs
        for (size_t i = 0; i < pdbs->size(); i++)
        {
            const shared_ptr<pdbs::PatternDatabase> &pdb = (*pdbs)[i];
            relevant_operators_by_restriction.emplace_back();
            vector<int> &curr = relevant_operators_by_restriction.back();
            for (OperatorProxy op : task_proxy.get_operators())
            {
                if (is_operator_relevant(pdb->get_pattern(), op))
                {
                    curr.push_back(op.get_id());
                }
            }

            if (curr.size() == 1)
            {
                this->simple_restrictions_ids.push_back(i);
            }
        }

        // relevant restrictions for each operator
        relevant_restrictions_by_operator.resize(operators.size());
        restriction_position_on_relevant_restrictions_by_operator.resize(operators.size());
        for (size_t i = 0; i < relevant_operators_by_restriction.size(); i++)
        {
            for (size_t j = 0; j < relevant_operators_by_restriction[i].size(); j++)
            {
                int restriction_id = i;
                int operator_id = relevant_operators_by_restriction[restriction_id][j];

                relevant_restrictions_by_operator[operator_id].push_back(restriction_id);
                restriction_position_on_relevant_restrictions_by_operator[operator_id].resize(restriction_id + 1);
                restriction_position_on_relevant_restrictions_by_operator[operator_id][restriction_id] = relevant_restrictions_by_operator[operator_id].size() - 1;
            }
        }

        // auxiliary vectors to heuristic computation
        value_pdbs.resize(pdbs->size());
        lower_bounds.resize(pdbs->size());
        operator_count.resize(operators.size());
    }

    int PostHoc::compute_heuristic(const State &ancestor_state)
    {
        State state = convert_ancestor_state(ancestor_state);
        this->state = &state;

        if (set_value_pdbs(state))
        {
            return DEAD_END;
        }

        for (size_t j = 0; j < operator_count.size(); j++)
            operator_count[j] = 0;

        for (size_t j = 0; j < value_pdbs.size(); j++)
            lower_bounds[j] = value_pdbs[j];

        compute_post_hoc();

        int h_value = 0;

        for (size_t i = 0; i < operator_count.size(); i++)
        {
            h_value += operator_cost[i] * operator_count[i];
        }

        return h_value;
    }

    int PostHoc::set_value_pdbs(const State &state)
    {
        for (size_t i = 0; i < pdbs->size(); ++i)
        {
            int h = (*pdbs)[i]->get_value(state.get_unpacked_values());

            if (h == numeric_limits<int>::max())
                return DEAD_END;

            value_pdbs[i] = h;
        }

        return 0;
    }

    void PostHoc::print_info()
    {
        utils::g_log << "Operators: " << operators.size() << endl;
        utils::g_log << "Restrictions: " << relevant_operators_by_restriction.size() << endl;

        if (relevant_restrictions_by_operator.size() > 0)
        {
            int mean_mentions = 0;
            for (size_t i = 0; i < relevant_restrictions_by_operator.size(); i++)
                mean_mentions += relevant_restrictions_by_operator[i].size();
            utils::g_log << "Mean mentions: " << (mean_mentions / relevant_restrictions_by_operator.size()) << endl;
        }

        if (relevant_operators_by_restriction.size() > 0)
        {
            int mean_operators = 0;
            for (size_t i = 0; i < relevant_operators_by_restriction.size(); i++)
                mean_operators += relevant_operators_by_restriction[i].size();
            utils::g_log << "Mean operators: " << (mean_operators / relevant_operators_by_restriction.size()) << endl;
        }
    }
}
