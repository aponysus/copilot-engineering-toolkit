using System;

namespace Synthetic.Distributions;

public sealed record DistributionResponse(decimal CashDist);

public sealed class DistributionController
{
    private readonly DistributionService service;

    public DistributionController(DistributionService service) => this.service = service;

    public DistributionResponse Get(int accountId, DateTime asOf) =>
        new DistributionResponse(service.GetCashDist(accountId, asOf));
}
