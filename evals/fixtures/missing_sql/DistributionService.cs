using System;
using System.Collections.Generic;

namespace Synthetic.Distributions;

public interface IProcedureClient
{
    IReadOnlyDictionary<string, decimal> QuerySingle(
        string procedure, IReadOnlyDictionary<string, object> parameters);
}

public sealed class DistributionService
{
    private readonly IProcedureClient database;

    public DistributionService(IProcedureClient database) => this.database = database;

    public decimal GetCashDist(int accountId, DateTime asOf)
    {
        var row = database.QuerySingle("sp_GetDistributions",
            new Dictionary<string, object> { ["AccountId"] = accountId, ["AsOf"] = asOf });
        return row["CashDist"];
    }
}
