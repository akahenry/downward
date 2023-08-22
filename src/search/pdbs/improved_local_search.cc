#include "improved_local_search.h"

#include "pattern_generator.h"
#include "utils.h"

#include "../option_parser.h"
#include "../plugin.h"

#include "../utils/logging.h"
#include "../utils/timer.h"

#include <iostream>
#include <limits>
#include <memory>

using namespace std;

namespace pdbs
{

    ImprovedLocalSearch::ImprovedLocalSearch(const Options &opts) : Heuristic(opts)
    {
        shared_ptr<PatternCollectionGenerator> pattern_generator =
            opts.get<shared_ptr<PatternCollectionGenerator>>("patterns");
        PatternCollectionInformation pci = pattern_generator->generate(task);

        this->heuristics = pci.get_pdbs();

        this->initialize_operators();
        this->initialize_count_variables();
        this->initialize_restrictions();
        this->initialize_relevant_operators();
    }

    void ImprovedLocalSearch::initialize_operators()
    {
        TaskProxy task_proxy = this->get_task_proxy();

        for (OperatorProxy op : task_proxy.get_operators())
        {
            this->operators.push_back({op.get_id(), op.get_cost()});
        }
    }

    void ImprovedLocalSearch::initialize_count_variables()
    {
        for (size_t i = 0; i < this->operators.size(); i++)
        {
            this->operator_count[i] = 0;
        }
    }

    void ImprovedLocalSearch::initialize_restrictions()
    {
        TaskProxy task_proxy = TaskProxy(*this->task);
        OperatorsProxy operators_proxy = task_proxy.get_operators();

        for (size_t heuristic_id = 0; heuristic_id < this->heuristics->size(); heuristic_id++)
        {
            std::shared_ptr<pdbs::PatternDatabase> &heuristic = this->heuristics->at(heuristic_id);
            // -1 because we can't get heuristic's value without a state and we don't have the state here yet
            Restriction restriction = {(int)heuristic_id, -1, std::vector<Operator *>()};

            for (size_t operator_id = 0; operator_id < operators_proxy.size(); operator_id++)
            {
                OperatorProxy operator_proxy = operators_proxy[operator_id];

                if (heuristic->is_operator_relevant(operator_proxy))
                {
                    restriction.operators.push_back(&this->operators[operator_id]);
                }
            }

            this->restrictions.push_back(restriction);
        }
    }

    void ImprovedLocalSearch::initialize_relevant_operators()
    {
        this->relevant_operators.resize(this->operators.size());

        for (size_t restriction_id = 0; restriction_id < this->restrictions.size(); restriction_id++)
        {
            for (const Operator *operator_ptr : this->restrictions[restriction_id].operators)
            {
                this->relevant_operators[operator_ptr->id].push_back(&this->restrictions[restriction_id]);
            }
        }
    }

    bool ImprovedLocalSearch::any_pricing_greater_than_zero()
    {
        for (const Restriction &restriction : this->restrictions)
        {
            if (restriction.pricing > 0)
            {
                return true;
            }
        }

        return false;
    }

    double ImprovedLocalSearch::sum_operator_performance(Operator op)
    {
        double acc = 0;

        for (const Restriction *restriction_ptr : this->relevant_operators[op.id])
        {
            acc += std::min((double)1, (double)(restriction_ptr->pricing / op.cost));
        }

        return acc;
    }

    Restriction ImprovedLocalSearch::get_restriction_with_minimum_pricing(Operator op)
    {
        Restriction restriction_with_minimum_pricing = *(this->relevant_operators[op.id][0]);

        for (size_t i = 1; i < this->relevant_operators[op.id].size(); i++)
        {
            if (restriction_with_minimum_pricing.pricing > this->relevant_operators[op.id][i]->pricing)
            {
                restriction_with_minimum_pricing = *(this->relevant_operators[op.id][i]);
            }
        }

        return restriction_with_minimum_pricing;
    }

    TaskProxy ImprovedLocalSearch::get_task_proxy()
    {
        if (!this->task_proxy_ptr)
        {
            this->task_proxy_ptr = new TaskProxy(*this->task);
        }

        return *(this->task_proxy_ptr);
    }

    int ImprovedLocalSearch::compute_heuristic(const State &ancestor_state)
    {
        State state = convert_ancestor_state(ancestor_state);

        if (set_heuristics_pricing(state))
        {
            return DEAD_END;
        }

        int a = 0;

        return generate_solution();
    }

    int ImprovedLocalSearch::generate_solution()
    {
        /*
            Inputs:
                - H: list of PDBs heuristics
                    - a PDB heuristic has its heuristic value and the list of operators that affects it
                - O: list of operators with their costs

            Intermediary variables:
                - X: map of variables representing the number of times each operator was used within the plan (operator's ID to number)
                - R: map of heuristics IDs to restrictions
                    - a restriction has a set of operators that affects it (operators) and its pricing (pricing)
                - O_relevant: map of operators IDs to operators for each operator that is still relevant for an iteration of the algorithm
                    - an operator is relevant if there's at least one still unsatisfied restriction considering the variable X
                - o_best_performance_max: maximum operator related pricings that can be achieved within the restrictions
                    - an operator related pricings is the sum of all restrictions' pricings divided by the operator's cost
                - o_best: the best operator to increment on the iteration
                - o_performance_related: a temporary variable used to store the operator pricings related for an operator
                - t_increment: the number of times that the chosen operator will be incremented

            1. X := {o.id: 0 for o in O}
            2. R := {h.id: {operators: set(filter(lambda o: h.is_affected_by(o), O)), pricing: h.value} for h in H}
            3. O_relevant := {o.id: {...o, restrictions: set(filter(lambda r: o in r.operators, R))} for o in O}
            4. while any([r.pricing > 0 for r in R]):
                // Initialize variables to choose the operator that will have increments in its X variable
                1. o_best_performance_max := 0
                2. o_best := null
                3. o_best_t_wo_lost := 0

                // Identify the best operator
                4. for o in O_relevant.values():
                    1. o_performance_related := sum([min(1, r.pricing / o.cost) for r in o.restrictions])
                    2. if o_best_performance_max < o_performance_related:
                        1. o_best_performance_max := o_performance_related
                        2. o_best := o

                    // Tie break considering how many times we can use each operator without losing performance
                    3. if o_best_performance_max == o_performance_related:
                        1. o_r_pricing_min := min([r.pricing for r in o.restrictions])
                        2. o_t_wo_lost := max(1, floor(r_pricing_min / o.cost))
                        3. o_t_stride := o_t_wo_lost * o.cost
                        6. o_best_t_stride := o_best_t_wo_lost * o_best.cost
                        7. if o_best_t_stride < o_t_stride:
                            1. o_best_performance_max := o_performance_related
                            2. o_best := o
                            3. o_best_t_wo_lost := o_t_wo_lost

                // Increment the operator X variable
                5. X[o_best.id] := X[o_best.id] + o_best_t_wo_lost

                // Update operators relevance considering the effect of the increment in the satisfaction of the restrictions that are affected by the chosen operator
                6. for r in o_best.restrictions:
                    1. r.pricing := r.pricing - (t_increment * o.cost)
                    2. if r.pricing <= 0:
                        1. for each o in r.operators:
                            1. O_relevant[o.id].restrictions := O_relevant[o.id].restrictions / r
        */
        while (this->any_pricing_greater_than_zero())
        {
            BestOperator best_operator;

            for (Operator &op : this->operators)
            {
                if (best_operator.op.id == -1)
                {
                    best_operator.op = op;
                    continue;
                }

                double performance = this->sum_operator_performance(op);
                Restriction minimum_pricing_restriction = this->get_restriction_with_minimum_pricing(op);
                int times_to_increment_without_lost = std::max(1, (int)std::floor(minimum_pricing_restriction.pricing / op.cost));

                if (best_operator.performance < performance)
                {
                    best_operator.performance = performance;
                    best_operator.op = op;
                }
                else if (best_operator.performance == performance)
                {
                    int stride = times_to_increment_without_lost * op.cost;
                    if (best_operator.get_stride() < stride)
                    {
                        best_operator.performance = performance;
                        best_operator.op = op;
                        best_operator.times_to_increment_without_lost = times_to_increment_without_lost;
                    }
                }
            }

            this->operator_count[best_operator.op.id] += best_operator.times_to_increment_without_lost;

            for (Restriction *restriction : this->relevant_operators[best_operator.op.id])
            {
                restriction->pricing -= (best_operator.times_to_increment_without_lost * best_operator.op.cost);
                if (restriction->pricing <= 0)
                {
                    for (const Operator *op : restriction->operators)
                    {
                        remove(this->relevant_operators[op->id].begin(), this->relevant_operators[op->id].end(), restriction);
                    }
                }
            }
        }

        int acc = 0;

        for (const Operator &op : this->operators)
        {
            acc += this->operator_count[op.id] * op.cost;
        }

        return acc;
    }

    int ImprovedLocalSearch::set_heuristics_pricing(const State &state)
    {
        for (size_t i = 0; i < this->heuristics->size(); i++)
        {
            int h = (*this->heuristics)[i]->get_value(state.get_unpacked_values());

            if (h == numeric_limits<int>::max())
                return DEAD_END;

            this->restrictions[i].pricing = h;
        }

        return 0;
    }

    static shared_ptr<Heuristic> _parse(OptionParser &parser)
    {
        parser.document_synopsis("", "");
        parser.document_language_support("action costs", "supported");
        parser.document_language_support("conditional effects", "not supported");
        parser.document_language_support("axioms", "not supported");
        parser.document_property("admissible", "no");
        parser.document_property("consistent", "no");
        parser.document_property("safe", "yes");
        parser.document_property("preferred operators", "no");

        parser.add_option<shared_ptr<PatternCollectionGenerator>>(
            "patterns",
            "pattern generation method",
            "systematic(4)");
        parser.add_option<int>(
            "n",
            "number of iterations of randomized order",
            "1",
            Bounds("1", "1000"));

        vector<string> order_opts;
        order_opts.push_back("sort");
        order_opts.push_back("random");
        order_opts.push_back("default");

        parser.add_enum_option<Order>("res_order",
                                      order_opts,
                                      "Restriction order",
                                      "default");

        parser.add_enum_option<Order>("op_order",
                                      order_opts,
                                      "Operator order",
                                      "default");

        vector<string> dec_opts;
        dec_opts.push_back("before");
        dec_opts.push_back("iterative");

        parser.add_enum_option<Decrement>("decrement",
                                          dec_opts,
                                          "Decrement mode",
                                          "iterative");

        parser.add_option<int>("seed",
                               "random seed",
                               "0",
                               Bounds("0", "2147483646"));

        parser.add_option<bool>(
            "ff",
            "",
            "false");

        parser.add_option<bool>(
            "preferred",
            "set preferred operators",
            "false");

        Heuristic::add_options_to_parser(parser);

        Options opts = parser.parse();
        if (parser.dry_run())
            return nullptr;

        return make_shared<ImprovedLocalSearch>(opts);
    }

    static Plugin<Evaluator> _plugin("ilsh", _parse, "heuristics_pdb");

    ImprovedLocalSearch::BestOperator::BestOperator()
    {
        this->op = {-1, -1};
        this->times_to_increment_without_lost = 0;
        this->performance = 0;
    }

    int ImprovedLocalSearch::BestOperator::get_stride()
    {
        return this->times_to_increment_without_lost * this->op.cost;
    }
}
