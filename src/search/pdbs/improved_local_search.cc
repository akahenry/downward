#include "improved_local_search.h"

#include "pattern_generator.h"
#include "utils.h"

#include "../plugins/options.h"
#include "../plugins/plugin.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    ImprovedLocalSearch::ImprovedLocalSearch(const plugins::Options &opts) : Heuristic(opts),
                                                                             seed(opts.get<int>("seed"))
    {
        std::srand(seed);

        shared_ptr<PatternCollectionGenerator> pattern_generator =
            opts.get<shared_ptr<PatternCollectionGenerator>>("patterns");
        PatternCollectionInformation pci = pattern_generator->generate(task);

        pdbs = pci.get_pdbs();

        get_restrictions();

        print_info();
    }

    void ImprovedLocalSearch::get_restrictions()
    {
        TaskProxy task_proxy = TaskProxy(*task);

        // operators and costs
        for (OperatorProxy op : task_proxy.get_operators())
        {
            operators.push_back(op.get_id());
            operator_cost.push_back(op.get_cost());
        }

        // restrictions from pdbs
        for (const shared_ptr<pdbs::PatternDatabase> &pdb : *pdbs)
        {
            restrictions.emplace_back();
            vector<int> &curr = restrictions.back();
            for (OperatorProxy op : task_proxy.get_operators())
            {
                if (is_operator_relevant(pdb->get_pattern(), op))
                {
                    curr.push_back(op.get_id());
                }
            }
        }

        // relevant restrictions for each operator
        restriction_operator.resize(operators.size());
        for (size_t i = 0; i < restrictions.size(); i++)
        {
            for (size_t j = 0; j < restrictions[i].size(); j++)
            {
                restriction_operator[restrictions[i][j]].push_back(i);
            }
        }

        // restriction ordering index
        restriction_order.resize(restrictions.size());
        for (size_t i = 0; i < restrictions.size(); i++)
            restriction_order[i] = i;

        // auxiliary vectors to heuristic computation
        value_pdbs.resize(pdbs->size());
        lower_bounds.resize(pdbs->size());
        operator_count.resize(operators.size());
    }

    int ImprovedLocalSearch::compute_heuristic(const State &ancestor_state)
    {
        State state = convert_ancestor_state(ancestor_state);

        if (set_value_pdbs(state))
        {
            return DEAD_END;
        }

        return generate_solution(state);
    }

    int ImprovedLocalSearch::generate_solution(const State &state)
    {
        for (size_t j = 0; j < operator_count.size(); j++)
            operator_count[j] = 0;

        for (size_t j = 0; j < value_pdbs.size(); j++)
            lower_bounds[j] = value_pdbs[j];

        for (const int id_res : restriction_order)
        {
            int var = 0;
            while (lower_bounds[id_res] > 0)
            {
                const int id_op = restrictions[id_res][var];
                operator_count[id_op]++;

                for (size_t i = 0; i < restriction_operator[id_op].size(); i++)
                    lower_bounds[restriction_operator[id_op][i]] -= operator_cost[id_op];

                var = (var + 1) % restrictions[id_res].size();
            }
        }

        int h_value = 0;

        for (size_t i = 0; i < operator_count.size(); i++)
        {
            h_value += operator_cost[i] * operator_count[i];
        }

        return h_value;
    }

    int ImprovedLocalSearch::set_value_pdbs(const State &state)
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

    void ImprovedLocalSearch::print_info()
    {
        utils::g_log << "Operators: " << operators.size() << endl;
        utils::g_log << "Restrictions: " << restrictions.size() << endl;

        if (restriction_operator.size() > 0)
        {
            int mean_mentions = 0;
            for (size_t i = 0; i < restriction_operator.size(); i++)
                mean_mentions += restriction_operator[i].size();
            utils::g_log << "Mean mentions: " << (mean_mentions / restriction_operator.size()) << endl;
        }

        if (restrictions.size() > 0)
        {
            int mean_operators = 0;
            for (size_t i = 0; i < restrictions.size(); i++)
                mean_operators += restrictions[i].size();
            utils::g_log << "Mean operators: " << (mean_operators / restrictions.size()) << endl;
        }
    }

    class ImprovedLocalSearchFeature : public plugins::TypedFeature<Evaluator, pdbs::ImprovedLocalSearch>
    {
    public:
        ImprovedLocalSearchFeature() : TypedFeature("ilsh")
        {
            document_title("ImprovedLocalSearch heuristic");

            add_option<shared_ptr<pdbs::PatternCollectionGenerator>>(
                "patterns",
                "pattern generation method",
                "systematic(4)");

            add_option<int>("seed",
                            "random seed",
                            "0",
                            plugins::Bounds("0", "2147483646"));

            Heuristic::add_options_to_feature(*this);

            document_language_support("action costs", "supported");
            document_language_support("conditional effects", "not supported");
            document_language_support("axioms", "not supported");
            document_property("admissible", "no");
            document_property("consistent", "no");
            document_property("safe", "yes");
            document_property("preferred operators", "no");
        }
    };
    static plugins::FeaturePlugin<ImprovedLocalSearchFeature> _plugin;
}
